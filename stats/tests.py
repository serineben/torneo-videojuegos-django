from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from games.models import Game
from players.models import Registration

User = get_user_model()


class HomeViewTests(TestCase):
    def setUp(self):
        self.player = User.objects.create_user(
            username="player",
            email="player@example.com",
            password="test-password",
            role=User.Role.PLAYER,
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="test-password",
            role=User.Role.ADMIN,
        )

    def test_home_is_available_to_anonymous_players_and_admins(self):
        for user in (None, self.player, self.admin):
            with self.subTest(user=user):
                self.client.logout()
                if user is not None:
                    self.client.force_login(user)

                response = self.client.get(reverse("home"))

                self.assertEqual(response.status_code, 200)

    def test_podium_is_only_in_context_for_authenticated_users(self):
        game = Game.objects.create(name="Chess")
        Registration.objects.create(user=self.player, game=game, points=10)

        anonymous_response = self.client.get(reverse("home"))
        self.assertNotIn("podium", anonymous_response.context)

        for user in (self.player, self.admin):
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(reverse("home"))

                self.assertIn("podium", response.context)
                self.assertEqual(
                    [row["user"] for row in response.context["podium"]],
                    [self.player],
                )


class ErrorPageTests(TestCase):
    def test_unknown_url_uses_custom_404_template(self):
        with override_settings(DEBUG=False):
            response = self.client.get("/this-page-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_player_accessing_games_receives_custom_403_template(self):
        player = User.objects.create_user(
            username="player",
            email="player@example.com",
            password="test-password",
            role=User.Role.PLAYER,
        )
        self.client.force_login(player)

        response = self.client.get("/juegos/")

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")

# Create your tests here.
