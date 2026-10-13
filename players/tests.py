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


class ParticipantListViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="test-password",
            role=User.Role.ADMIN,
        )
        self.client.force_login(self.admin)

    def create_player(self, username, email=None):
        return User.objects.create_user(
            username=username,
            email=email or f"{username}@example.com",
            password="test-password",
        )

    def get_participant_names(self, **params):
        response = self.client.get(reverse("participant_list"), params)
        self.assertEqual(response.status_code, 200)
        return [user.username for user in response.context["participants"]]

    def test_filters_by_username_case_insensitively(self):
        self.create_player("MiXeDName")
        self.create_player("another")

        self.assertEqual(self.get_participant_names(q="mixed"), ["MiXeDName"])

    def test_filters_by_email_case_insensitively(self):
        self.create_player("matching", "Contact-Needle@example.com")
        self.create_player("another", "other@example.com")

        self.assertEqual(self.get_participant_names(q="NEEDLE"), ["matching"])

    def test_filters_by_game(self):
        chess = Game.objects.create(name="Chess")
        go = Game.objects.create(name="Go")
        chess_player = self.create_player("chess_player")
        go_player = self.create_player("go_player")
        Registration.objects.create(user=chess_player, game=chess)
        Registration.objects.create(user=go_player, game=go)

        self.assertEqual(
            self.get_participant_names(game=str(chess.pk)),
            ["chess_player"],
        )

    def test_filters_by_level(self):
        game = Game.objects.create(name="Chess")
        amateur = self.create_player("amateur")
        expert = self.create_player("expert")
        Registration.objects.create(
            user=amateur,
            game=game,
            level=Registration.Level.AMATEUR,
        )
        Registration.objects.create(
            user=expert,
            game=game,
            level=Registration.Level.EXPERT,
        )

        self.assertEqual(
            self.get_participant_names(level=Registration.Level.AMATEUR),
            ["amateur"],
        )

    def test_game_and_level_must_match_the_same_registration(self):
        chess = Game.objects.create(name="Chess")
        go = Game.objects.create(name="Go")
        mismatched = self.create_player("mismatched")
        matching = self.create_player("matching")
        Registration.objects.create(
            user=mismatched,
            game=chess,
            level=Registration.Level.EXPERT,
        )
        Registration.objects.create(
            user=mismatched,
            game=go,
            level=Registration.Level.AMATEUR,
        )
        Registration.objects.create(
            user=matching,
            game=chess,
            level=Registration.Level.AMATEUR,
        )

        self.assertEqual(
            self.get_participant_names(
                game=str(chess.pk),
                level=Registration.Level.AMATEUR,
            ),
            ["matching"],
        )

    def test_filter_does_not_return_duplicate_participants(self):
        chess = Game.objects.create(name="Chess")
        go = Game.objects.create(name="Go")
        repeated = self.create_player("repeated")
        Registration.objects.create(
            user=repeated,
            game=chess,
            level=Registration.Level.AMATEUR,
        )
        Registration.objects.create(
            user=repeated,
            game=go,
            level=Registration.Level.AMATEUR,
        )

        self.assertEqual(
            self.get_participant_names(level=Registration.Level.AMATEUR),
            ["repeated"],
        )

    def test_paginates_ten_participants_per_page(self):
        for index in range(12):
            self.create_player(f"player{index:02}")

        first_page = self.client.get(reverse("participant_list"))
        second_page = self.client.get(reverse("participant_list"), {"page": 2})

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(first_page.context["participants"]), 10)
        self.assertEqual(len(second_page.context["participants"]), 2)
        self.assertTrue(first_page.context["is_paginated"])


class GameListViewTests(TestCase):
    def setUp(self):
        admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="test-password",
            role=User.Role.ADMIN,
        )
        self.client.force_login(admin)

    def test_searches_game_name_case_insensitively(self):
        Game.objects.create(name="Chess Club")
        Game.objects.create(name="Go")

        response = self.client.get(reverse("game_list"), {"q": "cHeSs"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [game.name for game in response.context["games"]],
            ["Chess Club"],
        )


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
