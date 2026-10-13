from django.test import TestCase
from django.urls import reverse

from config.testing import make_admin, make_game, make_registration, make_user


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player = make_user("player1")
        cls.g1, cls.g2 = make_game("A"), make_game("B")
        make_registration(cls.player, cls.g2, points=30)

    def setUp(self):
        self.client.force_login(self.player)
        self.url = reverse("dashboard")

    def test_default_game_is_the_first_one(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["selected_game"], self.g1)

    def test_select_game_by_query(self):
        response = self.client.get(self.url, {"game": self.g2.pk})
        self.assertEqual(response.context["selected_game"], self.g2)
        self.assertEqual(response.context["game_points"]["data"], [30])

    def test_invalid_game_parameter_does_not_crash(self):
        for value in ("abc", "99999"):
            with self.subTest(value=value):
                response = self.client.get(self.url, {"game": value})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["selected_game"], self.g1)

    def test_dashboard_without_data(self):
        self.g1.delete()
        self.g2.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["selected_game"])


class HomeTests(TestCase):
    def test_home_is_public(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("podium", response.context)

    def test_podium_for_authenticated_users(self):
        player = make_user("player1")
        make_registration(player, make_game(), points=40)
        for user in (player, make_admin()):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("home"))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context["podium"][0]["user"], player)


class ErrorPageTests(TestCase):
    def test_404_uses_custom_template(self):
        response = self.client.get("/esto-no-existe/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_403_uses_custom_template(self):
        self.client.force_login(make_user("player1"))
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")