from django import forms

from .models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ("name", "description", "image")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }