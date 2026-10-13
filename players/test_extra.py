from django.test import TestCase
from django.urls import reverse

from config.testing import make_admin, make_game, make_registration, make_user


class RegistrationViewExtraTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.player = make_user("player1")
        cls.game = make_game("Game A")
        cls.registration = make_registration(cls.player, cls.game)

    def setUp(self):
        self.client.force_login(self.admin)

    def test_registration_create_only_accepts_player_accounts(self):
        for user_id in (self.admin.pk, 999999):
            with self.subTest(user_id=user_id):
                response = self.client.get(
                    reverse("registration_create", args=[user_id])
                )
                self.assertEqual(response.status_code, 404)

    def test_registration_update_form_receives_owner_and_context(self):
        response = self.client.get(
            reverse("registration_update", args=[self.registration.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["participant"], self.player)
        self.assertEqual(response.context["form"].user, self.player)


class GamePointsViewExtraTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)
        self.game = make_game("Empty game")

    def test_points_page_for_game_without_registrations_has_empty_formset(self):
        response = self.client.get(reverse("game_points", args=[self.game.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["formset"].forms), 0)

    def test_points_and_game_ranking_return_404_for_unknown_game(self):
        for route_name in ("game_points", "game_ranking"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name, args=[999999]))
                self.assertEqual(response.status_code, 404)
