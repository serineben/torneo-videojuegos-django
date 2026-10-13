from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from config.testing import PASSWORD, make_user

VALID_DATA = {
    "username": "newuser",
    "email": "new@example.com",
    "password1": "Str0ngPass!2024",
    "password2": "Str0ngPass!2024",
}


class UserModelTests(TestCase):
    def test_default_role_is_player(self):
        self.assertEqual(make_user().role, User.Role.PLAYER)

    def test_superuser_is_always_admin(self):
        user = User.objects.create_superuser("root", "root@example.com", PASSWORD)
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_admin_role)

    def test_email_must_be_unique(self):
        make_user("a")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("b", email="a@example.com", password=PASSWORD)


class RegisterTests(TestCase):
    def test_register_creates_player_and_logs_in(self):
        response = self.client.post(reverse("register"), VALID_DATA, follow=True)
        user = User.objects.get(username="newuser")
        self.assertEqual(user.role, User.Role.PLAYER)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
        self.assertContains(response, "Cuenta creada correctamente")

    def test_role_field_cannot_be_injected(self):
        self.client.post(reverse("register"), {**VALID_DATA, "role": "admin"})
        self.assertEqual(User.objects.get(username="newuser").role, User.Role.PLAYER)

    def test_duplicate_email_is_rejected(self):
        make_user("other")
        data = {**VALID_DATA, "email": "other@example.com"}
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_password_mismatch_is_rejected(self):
        data = {**VALID_DATA, "password2": "otra-cosa-123"}
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = make_user("alice")

    def test_login_ok_shows_message(self):
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": PASSWORD}, follow=True
        )
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)
        self.assertContains(response, "Has iniciado sesión correctamente")

    def test_login_wrong_password(self):
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": "incorrecta"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_authenticated_user_is_redirected_from_login(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("login")).status_code, 302)

    def test_logout_by_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)