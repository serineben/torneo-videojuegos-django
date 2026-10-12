from django import forms
from django.contrib.auth.forms import UserCreationForm

from accounts.models import User
from .models import Registration
from django.forms import modelformset_factory



class ParticipantCreateForm(UserCreationForm):
    """Admin creates a participant (role is always player)."""

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["username"].label = "Nombre de usuario"
        self.fields["email"].label = "Correo electrónico"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Repetir contraseña"


class ParticipantUpdateForm(forms.ModelForm):
    """Admin edits a participant (no password here)."""

    class Meta:
        model = User
        fields = ("username", "email", "is_active")
        labels = {
            "username": "Nombre de usuario",
            "email": "Correo electrónico",
            "is_active": "Cuenta activa",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ("game", "level")
        widgets = {
            "game": forms.Select(attrs={"class": "form-select"}),
            "level": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_game(self):
        game = self.cleaned_data["game"]
        qs = Registration.objects.filter(user=self.user, game=game)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este participante ya está inscrito en este juego.")
        return game

PointsFormSet = modelformset_factory(
    Registration,
    fields=("points",),
    extra=0,
    widgets={
        "points": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
    },
)