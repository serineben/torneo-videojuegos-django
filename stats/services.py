from django.db.models import Avg, Count

from accounts.models import User
from games.models import Game
from players.models import Registration
from players.services import game_ranking, general_ranking


def summary():
    return {
        "participants": User.objects.filter(role=User.Role.PLAYER).count(),
        "games": Game.objects.count(),
        "registrations": Registration.objects.count(),
        "scored": Registration.objects.filter(points__isnull=False).count(),
    }


def top_players(limit=10):
    rows = general_ranking()[:limit]
    return {
        "labels": [r["user"].username for r in rows],
        "data": [r["total_points"] for r in rows],
    }


def level_distribution():
    counts = dict(
        Registration.objects.order_by().values_list("level").annotate(n=Count("id"))
    )
    return {
        "labels": [label for _, label in Registration.Level.choices],
        "data": [counts.get(value, 0) for value, _ in Registration.Level.choices],
    }


def registrations_per_game():
    games = Game.objects.annotate(n=Count("registrations")).order_by("name")
    return {"labels": [g.name for g in games], "data": [g.n for g in games]}


def average_points_per_game():
    games = Game.objects.annotate(avg=Avg("registrations__points")).order_by("name")
    return {
        "labels": [g.name for g in games],
        "data": [round(g.avg, 1) if g.avg is not None else 0 for g in games],
    }


def points_for_game(game):
    rows = game_ranking(game)
    return {
        "labels": [r["registration"].user.username for r in rows],
        "data": [r["registration"].points for r in rows],
    }