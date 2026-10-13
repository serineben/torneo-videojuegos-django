from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm
from .models import User

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Cuenta creada correctamente. ¡Bienvenido!")
        return response


class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    success_message = "Has iniciado sesión correctamente."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            field.widget.attrs["class"] = "form-control"
        return form