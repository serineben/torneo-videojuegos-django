from django.test import TestCase
from django.urls import reverse

from .forms import RegisterForm
from .models import User


class RegisterViewTests(TestCase):
    def test_form_contains_expected_fields(self):
        response = self.client.get(reverse("register"))

        self.assertEqual(
            list(response.context["form"].fields),
            ["username", "email", "password1", "password2"],
        )
        self.assertIsInstance(response.context["form"], RegisterForm)

    def test_registration_creates_player_logs_in_and_redirects_home(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newplayer",
                "email": "newplayer@example.com",
                "password1": "StrongPassword!942",
                "password2": "StrongPassword!942",
                "role": User.Role.ADMIN,
            },
        )

        user = User.objects.get(username="newplayer")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(user.role, User.Role.PLAYER)
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))
