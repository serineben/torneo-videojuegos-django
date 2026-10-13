from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from accounts.models import User
from games.models import Game


class SeedCommandTests(TestCase):
    def run_seed(self, **options):
        call_command("seed", stdout=StringIO(), **options)

    def demo_count(self):
        return User.objects.filter(username__startswith="demo_").count()

    def test_creates_demo_data(self):
        self.run_seed(players=3)
        self.assertEqual(self.demo_count(), 3)
        self.assertEqual(Game.objects.count(), 5)

    def test_is_idempotent(self):
        self.run_seed(players=3)
        self.run_seed(players=3)
        self.assertEqual(self.demo_count(), 3)
        self.assertEqual(Game.objects.count(), 5)

    def test_clear_removes_previous_demo_players(self):
        self.run_seed(players=5)
        self.run_seed(players=2, clear=True)
        self.assertEqual(self.demo_count(), 2)
        