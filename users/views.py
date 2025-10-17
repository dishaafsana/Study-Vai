from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = CustomUserCreationForm()
    return render(request, "auth/signup.html", {"form": form})


def TeamLeader_class_call(request):
    return render(request, "users/TeamLeaderclasscall.html")


def edit_student_profile(request):
    student = request.user
    if request.method == "POST":
        # Update fields from POST data
        student.class_name = request.POST.get("class_name", student.class_name)
        student.school_name = request.POST.get("school_name", student.school_name)
        student.address = request.POST.get("address", student.address)
        student.parent_phone = request.POST.get("parent_phone", student.parent_phone)
        email = request.POST.get("email", student.email)
        if email:
            student.email = email
            if hasattr(student, "user"):
                student.user.email = email
                student.user.save()
        # Handle profile picture upload
        if "profile_picture" in request.FILES:
            student.profile_picture = request.FILES["profile_picture"]
        student.save()
        return redirect("users:student_profile")
    return render(request, "users/edit_student_profile.html", {"student": student})


@login_required
def edit_TeamLeader_profile(request):
    TeamLeader = request.user
    if request.method == "POST":
        TeamLeader.qualification = request.POST.get("qualification", TeamLeader.qualification)
        TeamLeader.subjects_taught = request.POST.get("subjects_taught", TeamLeader.subjects_taught)
        TeamLeader.address = request.POST.get("address", TeamLeader.address)
        TeamLeader.phone_number = request.POST.get("phone_number", TeamLeader.phone_number)
        email = request.POST.get("email", TeamLeader.email)
        if email:
            TeamLeader.email = email
        if "profile_picture" in request.FILES:
            TeamLeader.profile_picture = request.FILES["profile_picture"]
        TeamLeader.save()
        return redirect("users:TeamLeader_profile")
    return render(request, "users/edit_TeamLeader_profile.html", {"TeamLeader": TeamLeader})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = request.POST.get("username")  # This is the email field
            password = request.POST.get("password")
            user = authenticate(request, username=email, password=password)  # <-- FIXED HERE
            if user is not None:
                login(request, user)
                # Redirect based on user_type
                if user.user_type == "student":
                    return redirect("users:student_profile")
                elif user.user_type == "TeamLeader":
                    return redirect("users:TeamLeader_profile")
        else:
            print(form.errors)  # Add this for debugging
    else:
        form = CustomAuthenticationForm()
    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("users:login")


@login_required
def student_profile(request):
    student = request.user
    return render(request, "users/studentProfile.html", {"student": student})


@login_required
def TeamLeader_profile(request):
    TeamLeader = request.user
    return render(request, "users/TeamLeaderProfile.html", {"TeamLeader": TeamLeader})


def student_marks(request):
    return render(request, "users/student_marks.html")


# Create your views here.
def learner(request):
    return render(request, "users/learner.html")


def TeamLeader(request):
    return render(request, "users/TeamLeader.html")


# Contact Page View
def contact(request):
    return render(request, "users/contact.html")
