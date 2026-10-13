from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from config.testing import make_user


class AuthenticationViewsExtraTests(TestCase):
    def test_login_form_applies_bootstrap_class_to_every_field(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        for field in response.context["form"].fields.values():
            with self.subTest(field=field.label):
                self.assertEqual(field.widget.attrs["class"], "form-control")

    def test_invalid_registration_keeps_form_errors_and_creates_no_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "invalid-user",
                "email": "not-an-email",
                "password1": "Str0ngPass!2024",
                "password2": "Str0ngPass!2024",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(User.objects.filter(username="invalid-user").exists())

    def test_login_with_unknown_username_does_not_authenticate(self):
        make_user("existing")

        response = self.client.post(
            reverse("login"),
            {"username": "missing", "password": "Pass12345!"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertNotIn("_auth_user_id", self.client.session)
