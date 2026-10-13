from django.test import TestCase
from django.urls import reverse

from config.testing import make_admin, make_game, make_registration, make_user
from games.models import Game
from players.models import Registration


class GameModelTests(TestCase):
    def test_str_and_ordering(self):
        make_game("Zelda")
        make_game("Asteroids")
        self.assertEqual([str(g) for g in Game.objects.all()], ["Asteroids", "Zelda"])


class GameCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()

    def setUp(self):
        self.client.force_login(self.admin)

    def test_create_game(self):
        response = self.client.post(reverse("game_create"), {"name": "Pong", "description": "Retro"})
        self.assertRedirects(response, reverse("game_list"))
        self.assertTrue(Game.objects.filter(name="Pong").exists())

    def test_duplicate_name_is_rejected(self):
        make_game("Pong")
        response = self.client.post(reverse("game_create"), {"name": "Pong"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.filter(name="Pong").count(), 1)

    def test_update_game(self):
        game = make_game("Pong")
        self.client.post(reverse("game_update", args=[game.pk]), {"name": "Pong 2", "description": ""})
        game.refresh_from_db()
        self.assertEqual(game.name, "Pong 2")

    def test_delete_game_removes_its_registrations(self):
        game = make_game("Pong")
        make_registration(make_user("a"), game)
        self.client.post(reverse("game_delete", args=[game.pk]))
        self.assertFalse(Game.objects.filter(pk=game.pk).exists())
        self.assertEqual(Registration.objects.count(), 0)

    def test_detail_lists_registrations_best_first(self):
        game = make_game("Pong")
        make_registration(make_user("low"), game, points=10)
        make_registration(make_user("high"), game, points=90)
        response = self.client.get(reverse("game_detail", args=[game.pk]))
        names = [r.user.username for r in response.context["registrations"]]
        self.assertEqual(names, ["high", "low"])


class GameListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()

    def setUp(self):
        self.client.force_login(self.admin)
        self.url = reverse("game_list")

    def test_search_by_name(self):
        for name in ("Tetris", "Mario Kart", "Mario Party"):
            make_game(name)
        response = self.client.get(self.url, {"q": "mario"})
        self.assertEqual(len(response.context["games"]), 2)

    def test_pagination_by_10(self):
        for i in range(12):
            make_game(f"Game {i:02d}")
        self.assertEqual(len(self.client.get(self.url).context["games"]), 10)
        self.assertEqual(len(self.client.get(self.url, {"page": 2}).context["games"]), 2)
        self.assertEqual(self.client.get(self.url, {"page": 3}).status_code, 404)