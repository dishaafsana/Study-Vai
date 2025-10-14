from django import forms
from .models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "description", "module_code", "pages", "file"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
