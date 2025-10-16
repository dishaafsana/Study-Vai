import os
from django.urls import reverse
from django.contrib import messages
from django.http import FileResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Note, Report
from django.shortcuts import redirect
from .forms import NoteForm
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse


def notes(request):
    notes = Note.objects.all().order_by("-upload_date")
    return render(request, "notes/notes.html", {"notes": notes})


@login_required
def download_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    try:
        file_path = note.file.path
    except ValueError:
        raise Http404("File path is invalid.")

    if os.path.exists(file_path):
        note.download_count = note.download_count + 1
        note.save(update_fields=["download_count"])
        return FileResponse(
            open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path)
        )
    else:
        raise Http404("File not found.")


@login_required
def report_note(request, note_id):
    # Accepts both form-encoded and JSON POSTs from client-side modal
    if request.method == "POST":
        note = get_object_or_404(Note, id=note_id)
        # Try JSON body first
        try:
            import json

            payload = json.loads(request.body.decode("utf-8")) if request.body else {}
            reason = payload.get("reason", "")
        except Exception:
            reason = request.POST.get("reason", "")

        Report.objects.create(note=note, reported_by=request.user, reason=reason)
        messages.success(request, "Thank you for your report. We will review it shortly.")
        # If AJAX/JSON, return JSON response
        if (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or request.content_type == "application/json"
        ):
            return JsonResponse({"status": "ok"})
        return HttpResponseRedirect(reverse("notes"))
    return HttpResponseRedirect(reverse("notes"))


def is_teamleader(user):
    return getattr(user, "user_type", None) == "TeamLeader"


@login_required
@user_passes_test(is_teamleader)
def add_note(request):
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.uploaded_by = request.user
            note.save()
            messages.success(request, "Note added successfully.")
            return redirect("notes")
    else:
        form = NoteForm()
    return render(request, "notes/add_note.html", {"form": form})


@login_required
@user_passes_test(is_teamleader)
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully.")
            return redirect("notes")
    else:
        form = NoteForm(instance=note)
    return render(request, "notes/edit_note.html", {"form": form, "note": note})


@login_required
@user_passes_test(is_teamleader)
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == "POST":
        # remove file from storage if exists
        try:
            if note.file and note.file.path and os.path.exists(note.file.path):
                os.remove(note.file.path)
        except Exception:
            pass
        note.delete()
        messages.success(request, "Note deleted.")
        return redirect("notes")
    return render(request, "notes/confirm_delete.html", {"note": note})
