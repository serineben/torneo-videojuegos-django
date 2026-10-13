from django.test import TestCase
from django.urls import reverse

from config.testing import make_admin, make_game, make_registration, make_user


class AccessControlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.player = make_user("player1")
        cls.game = make_game()
        cls.reg = make_registration(cls.player, cls.game)

    def admin_urls(self):
        return [
            reverse("game_list"),
            reverse("game_create"),
            reverse("game_detail", args=[self.game.pk]),
            reverse("game_update", args=[self.game.pk]),
            reverse("game_delete", args=[self.game.pk]),
            reverse("participant_list"),
            reverse("participant_create"),
            reverse("participant_detail", args=[self.player.pk]),
            reverse("participant_update", args=[self.player.pk]),
            reverse("participant_delete", args=[self.player.pk]),
            reverse("registration_create", args=[self.player.pk]),
            reverse("registration_update", args=[self.reg.pk]),
            reverse("registration_delete", args=[self.reg.pk]),
            reverse("game_points", args=[self.game.pk]),
            reverse("game_ranking", args=[self.game.pk]),
            reverse("general_ranking"),
        ]

    def player_urls(self):
        return [
            reverse("my_profile"),
            reverse("my_registration_create"),
            reverse("my_registration_delete", args=[self.reg.pk]),
        ]

    def test_anonymous_is_redirected_to_login(self):
        urls = self.admin_urls() + self.player_urls() + [reverse("dashboard")]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith(reverse("login")))

    def test_player_gets_403_on_admin_urls(self):
        self.client.force_login(self.player)
        for url in self.admin_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_admin_can_open_admin_urls(self):
        self.client.force_login(self.admin)
        for url in self.admin_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_admin_gets_403_on_player_urls(self):
        self.client.force_login(self.admin)
        for url in self.player_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_player_can_open_player_urls(self):
        self.client.force_login(self.player)
        for url in self.player_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_dashboard_is_open_to_both_roles(self):
        for user in (self.admin, self.player):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                self.assertEqual(self.client.get(reverse("dashboard")).status_code, 200)