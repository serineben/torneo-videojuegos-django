from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap styling on every field
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        self.fields["username"].label = "Nombre de usuario"
        self.fields["email"].label = "Correo electrónico"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Repetir contraseña"