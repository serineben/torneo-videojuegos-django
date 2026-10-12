from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from games.models import Game
from .models import Registration
from .services import game_ranking, general_ranking


User = get_user_model()


class RegistrationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="player",
            email="player@example.com",
            password="test-password",
        )
        self.game = Game.objects.create(name="Chess")

    def test_user_cannot_register_twice_for_same_game(self):
        Registration.objects.create(user=self.user, game=self.game)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Registration.objects.create(user=self.user, game=self.game)

    def test_amateur_normal_and_expert_are_valid_levels(self):
        valid_levels = {"amateur", "normal", "expert"}
        choices = {value for value, _label in Registration.Level.choices}

        self.assertEqual(choices, valid_levels)
        for level in valid_levels:
            with self.subTest(level=level):
                registration = Registration(
                    user=self.user,
                    game=self.game,
                    level=level,
                )
                registration.full_clean()

    def test_unknown_level_is_invalid(self):
        registration = Registration(
            user=self.user,
            game=self.game,
            level="beginner",
        )

        with self.assertRaises(ValidationError):
            registration.full_clean()


class ParticipantListPermissionTests(TestCase):
    def test_player_receives_forbidden_response(self):
        player = User.objects.create_user(
            username="player",
            email="player@example.com",
            password="test-password",
            role=User.Role.PLAYER,
        )
        self.client.force_login(player)

        response = self.client.get(reverse("participant_list"))

        self.assertEqual(response.status_code, 403)


class RankingServiceTests(TestCase):
    def create_player(self, username):
        return User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="test-password",
        )

    def register(self, user, game, points):
        return Registration.objects.create(user=user, game=game, points=points)

    def test_game_ranking_orders_by_points_and_shares_positions_for_ties(self):
        game = Game.objects.create(name="Chess")
        alice = self.create_player("alice")
        bob = self.create_player("bob")
        carol = self.create_player("carol")
        dave = self.create_player("dave")
        unscored = self.create_player("unscored")
        self.register(alice, game, 100)
        self.register(carol, game, 70)
        self.register(bob, game, 70)
        self.register(dave, game, 40)
        self.register(unscored, game, None)

        ranking = game_ranking(game)

        self.assertEqual(
            [
                (item["position"], item["registration"].user.username, item["registration"].points)
                for item in ranking
            ],
            [
                (1, "alice", 100),
                (2, "bob", 70),
                (2, "carol", 70),
                (4, "dave", 40),
            ],
        )

    def test_general_ranking_sums_points_across_games_and_shares_ties(self):
        chess = Game.objects.create(name="Chess")
        go = Game.objects.create(name="Go")
        alice = self.create_player("alice")
        bob = self.create_player("bob")
        carol = self.create_player("carol")
        unscored = self.create_player("unscored")
        self.register(alice, chess, 100)
        self.register(alice, go, 50)
        self.register(bob, chess, 75)
        self.register(bob, go, 75)
        self.register(carol, chess, 80)
        self.register(carol, go, None)
        self.register(unscored, chess, None)

        ranking = general_ranking()

        self.assertEqual(
            [
                (item["position"], item["user"].username, item["total_points"])
                for item in ranking
            ],
            [
                (1, "alice", 150),
                (1, "bob", 150),
                (3, "carol", 80),
            ],
        )
