from django.test import TestCase
from django.urls import reverse

from config.testing import make_game, make_registration, make_user
from players.models import Registration


class MyProfileTests(TestCase):
    def test_profile_shows_totals_and_position(self):
        player, other = make_user("player1"), make_user("other")
        game = make_game()
        make_registration(player, game, points=50)
        make_registration(other, game, points=80)
        self.client.force_login(player)
        response = self.client.get(reverse("my_profile"))
        self.assertEqual(response.context["total_points"], 50)
        self.assertEqual(response.context["general_position"], 2)

    def test_profile_does_not_show_other_players_registrations(self):
        player, other = make_user("player1"), make_user("other")
        make_registration(other, make_game("Secret Game"), points=10)
        self.client.force_login(player)
        response = self.client.get(reverse("my_profile"))
        self.assertEqual(response.context["rows"], [])
        self.assertNotContains(response, "Secret Game")


class SelfRegistrationTests(TestCase):
    def setUp(self):
        self.player = make_user("player1")
        self.other = make_user("other")
        self.game = make_game("Pong")
        self.client.force_login(self.player)
        self.url = reverse("my_registration_create")

    def test_player_can_register(self):
        response = self.client.post(self.url, {"game": self.game.pk, "level": "expert"})
        self.assertRedirects(response, reverse("my_profile"))
        reg = Registration.objects.get(game=self.game)
        self.assertEqual((reg.user, reg.level), (self.player, "expert"))

    def test_cannot_register_twice_in_same_game(self):
        make_registration(self.player, self.game)
        response = self.client.post(self.url, {"game": self.game.pk, "level": "normal"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ya está inscrito")
        self.assertEqual(Registration.objects.count(), 1)

    def test_cannot_register_someone_else(self):
        self.client.post(self.url, {"game": self.game.pk, "level": "normal", "user": self.other.pk})
        self.assertTrue(Registration.objects.filter(user=self.player).exists())
        self.assertFalse(Registration.objects.filter(user=self.other).exists())

    def test_points_cannot_be_set_by_the_player(self):
        self.client.post(self.url, {"game": self.game.pk, "level": "normal", "points": 999})
        self.assertIsNone(Registration.objects.get(user=self.player).points)


class CancelRegistrationTests(TestCase):
    def setUp(self):
        self.player = make_user("player1")
        self.other = make_user("other")
        self.client.force_login(self.player)

    def test_cancel_own_registration_without_points(self):
        reg = make_registration(self.player, make_game("A"))
        response = self.client.post(reverse("my_registration_delete", args=[reg.pk]))
        self.assertRedirects(response, reverse("my_profile"))
        self.assertFalse(Registration.objects.filter(pk=reg.pk).exists())

    def test_cannot_cancel_registration_with_points(self):
        reg = make_registration(self.player, make_game("A"), points=10)
        response = self.client.post(reverse("my_registration_delete", args=[reg.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Registration.objects.filter(pk=reg.pk).exists())

    def test_cannot_cancel_someone_elses_registration(self):
        reg = make_registration(self.other, make_game("A"))
        response = self.client.post(reverse("my_registration_delete", args=[reg.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Registration.objects.filter(pk=reg.pk).exists())