from django.contrib.auth.decorators import login_required


@login_required
def join_group(request, pk):
    group_instance = get_object_or_404(Group, pk=pk)
    user = request.user
    if user.user_type == "student":
        user.joined_group = group_instance
        user.save()
        return redirect("users:student_marks")
    return redirect("Group_detail", pk=pk)


from django.shortcuts import render
from .models import Group
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GroupForm
from .forms import GroupDeleteForm
from .forms import GroupUpdateForm


# Groups Page View
def Groups(request):
    Groups = Group.objects.all()
    print(Groups)
    return render(request, "courses/Groups.html", {"Groups": Groups})


def Group_detail(request, pk):
    group_instance = get_object_or_404(Group, pk=pk)
    # The members are available via the reverse relationship 'members'
    # Django will automatically fetch them when the template uses Group.members.all
    return render(request, "courses/Group details.html", {"Group": group_instance})


# In your Groups/views.py
def add_Group(request):
    if request.method == "POST":
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("Groups")  # or wherever you want to redirect
    else:
        form = GroupForm()
    return render(request, "courses/addGroups.html", {"form": form})


def update_Group(request, pk):
    group_instance = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        form = GroupUpdateForm(request.POST, request.FILES, instance=group_instance)
        if form.is_valid():
            form.save()
            return redirect("Group_detail", group_instance.id)
    else:
        form = GroupUpdateForm(instance=group_instance)
    return render(request, "courses/updateGroup.html", {"form": form, "Group": group_instance})


def delete_Group(request, pk):
    group_instance = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        group_instance.delete()
        return redirect("Groups")
    form = GroupDeleteForm(instance=group_instance)
    return render(request, "courses/Groupdelete.html", {"form": form, "Group": group_instance})
