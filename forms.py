from django import forms
from .models import Group


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = [
            "title",
            "instructor",
            "category",
            "image",
        ]


class GroupUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = [
            "title",
            "image",
            "category",
            "instructor",
        ]


class GroupDeleteForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = []  # No fields needed, just for confirmation
