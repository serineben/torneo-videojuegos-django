from django.db import IntegrityError, transaction
from django.test import TestCase

from config.testing import make_admin, make_game, make_registration, make_user
from players.models import Registration
from players.services import game_ranking, general_ranking, player_summary


class RegistrationModelTests(TestCase):
    def test_valid_levels(self):
        self.assertEqual(Registration.Level.values, ["amateur", "normal", "expert"])

    def test_user_cannot_join_same_game_twice(self):
        user, game = make_user("a"), make_game()
        make_registration(user, game)
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_registration(user, game)

    def test_str(self):
        reg = make_registration(make_user("a"), make_game("Pong"), Registration.Level.EXPERT)
        self.assertEqual(str(reg), "a - Pong (Expert)")


class GameRankingTests(TestCase):
    def setUp(self):
        self.game = make_game("Tetris")

    def test_empty(self):
        self.assertEqual(game_ranking(self.game), [])

    def test_orders_by_points_descending(self):
        make_registration(make_user("a"), self.game, points=10)
        make_registration(make_user("b"), self.game, points=30)
        make_registration(make_user("c"), self.game, points=20)
        names = [r["registration"].user.username for r in game_ranking(self.game)]
        self.assertEqual(names, ["b", "c", "a"])

    def test_ties_share_position(self):
        make_registration(make_user("a"), self.game, points=50)
        make_registration(make_user("b"), self.game, points=50)
        make_registration(make_user("c"), self.game, points=30)
        positions = [r["position"] for r in game_ranking(self.game)]
        self.assertEqual(positions, [1, 1, 3])

    def test_ignores_registrations_without_points(self):
        make_registration(make_user("a"), self.game, points=10)
        make_registration(make_user("b"), self.game, points=None)
        self.assertEqual(len(game_ranking(self.game)), 1)

    def test_points_zero_counts_as_a_result(self):
        make_registration(make_user("a"), self.game, points=0)
        self.assertEqual(len(game_ranking(self.game)), 1)


class GeneralRankingTests(TestCase):
    def setUp(self):
        self.g1, self.g2 = make_game("A"), make_game("B")

    def test_sums_points_across_games(self):
        alice, bob = make_user("alice"), make_user("bob")
        make_registration(alice, self.g1, points=30)
        make_registration(alice, self.g2, points=40)
        make_registration(bob, self.g1, points=60)
        ranking = general_ranking()
        self.assertEqual([r["user"].username for r in ranking], ["alice", "bob"])
        self.assertEqual([r["total_points"] for r in ranking], [70, 60])

    def test_ties_share_position(self):
        make_registration(make_user("a"), self.g1, points=50)
        make_registration(make_user("b"), self.g1, points=50)
        make_registration(make_user("c"), self.g1, points=10)
        self.assertEqual([r["position"] for r in general_ranking()], [1, 1, 3])

    def test_ignores_admins_and_players_without_points(self):
        make_registration(make_admin(), self.g1, points=99)
        make_registration(make_user("a"), self.g1, points=None)
        self.assertEqual(general_ranking(), [])


class PlayerSummaryTests(TestCase):
    def test_summary(self):
        g1, g2 = make_game("A"), make_game("B")
        alice, bob = make_user("alice"), make_user("bob")
        make_registration(alice, g1, points=50)
        make_registration(alice, g2, points=None)
        make_registration(bob, g1, points=80)

        summary = player_summary(alice)
        positions = [row["position"] for row in summary["rows"]]
        self.assertEqual(positions, [2, None])  # rows are ordered by game name
        self.assertEqual(summary["total_points"], 50)
        self.assertEqual(summary["general_position"], 2)

    def test_player_without_points(self):
        summary = player_summary(make_user("alice"))
        self.assertEqual(summary["rows"], [])
        self.assertIsNone(summary["total_points"])
        self.assertIsNone(summary["general_position"])