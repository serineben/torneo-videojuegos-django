from django.test import TestCase

from config.testing import make_admin, make_game, make_registration, make_user
from players.models import Registration
from stats import services


class SummaryTests(TestCase):
    def test_summary_counts(self):
        make_admin()  # admins are not participants
        a, b = make_user("a"), make_user("b")
        g1, g2 = make_game("A"), make_game("B")
        make_registration(a, g1, points=10)
        make_registration(a, g2)
        make_registration(b, g1, points=20)
        self.assertEqual(
            services.summary(),
            {"participants": 2, "games": 2, "registrations": 3, "scored": 2},
        )

    def test_summary_empty(self):
        self.assertEqual(
            services.summary(),
            {"participants": 0, "games": 0, "registrations": 0, "scored": 0},
        )


class ChartDataTests(TestCase):
    def test_level_distribution_always_has_three_levels(self):
        self.assertEqual(
            services.level_distribution(),
            {"labels": ["Amateur", "Normal", "Expert"], "data": [0, 0, 0]},
        )

    def test_level_distribution_counts(self):
        game = make_game()
        make_registration(make_user("a"), game, Registration.Level.EXPERT)
        make_registration(make_user("b"), game, Registration.Level.EXPERT)
        make_registration(make_user("c"), game, Registration.Level.AMATEUR)
        self.assertEqual(services.level_distribution()["data"], [1, 0, 2])

    def test_registrations_per_game(self):
        g1, g2 = make_game("A"), make_game("B")
        make_registration(make_user("a"), g1)
        make_registration(make_user("b"), g1)
        self.assertEqual(
            services.registrations_per_game(),
            {"labels": ["A", "B"], "data": [2, 0]},
        )

    def test_average_points_ignores_registrations_without_points(self):
        g1, g2 = make_game("A"), make_game("B")
        make_registration(make_user("a"), g1, points=10)
        make_registration(make_user("b"), g1, points=None)
        make_registration(make_user("c"), g1, points=20)
        self.assertEqual(
            services.average_points_per_game(),
            {"labels": ["A", "B"], "data": [15.0, 0]},
        )

    def test_top_players_respects_limit_and_order(self):
        game = make_game()
        make_registration(make_user("a"), game, points=50)
        make_registration(make_user("b"), game, points=80)
        make_registration(make_user("c"), game, points=20)
        self.assertEqual(
            services.top_players(limit=2),
            {"labels": ["b", "a"], "data": [80, 50]},
        )

    def test_points_for_game(self):
        game = make_game()
        make_registration(make_user("a"), game, points=10)
        make_registration(make_user("b"), game, points=30)
        self.assertEqual(
            services.points_for_game(game),
            {"labels": ["b", "a"], "data": [30, 10]},
        )