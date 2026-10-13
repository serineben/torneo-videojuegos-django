from django.db.models import Sum

from accounts.models import User
from .models import Registration


def game_ranking(game):
    """Return registrations of a game that have points, ordered best first, with a position."""
    registrations = (
        Registration.objects.filter(game=game, points__isnull=False)
        .select_related("user")
        .order_by("-points", "user__username")
    )
    ranking = []
    previous_points = None
    position = 0
    for index, reg in enumerate(registrations, start=1):
        # Same points = same position (ties)
        if reg.points != previous_points:
            position = index
            previous_points = reg.points
        ranking.append({"position": position, "registration": reg})
    return ranking


def general_ranking():
    """Return players ordered by total points across all games."""
    users = (
        User.objects.filter(role=User.Role.PLAYER, registrations__points__isnull=False)
        .annotate(total_points=Sum("registrations__points"))
        .order_by("-total_points", "username")
    )
    ranking = []
    previous_points = None
    position = 0
    for index, user in enumerate(users, start=1):
        if user.total_points != previous_points:
            position = index
            previous_points = user.total_points
        ranking.append({"position": position, "user": user, "total_points": user.total_points})
    return ranking



def player_summary(user):
    """Registrations of a player with their position per game, plus overall position."""
    rows = []
    for reg in user.registrations.select_related("game").order_by("game__name"):
        position = None
        if reg.points is not None:
            for item in game_ranking(reg.game):
                if item["registration"].pk == reg.pk:
                    position = item["position"]
                    break
        rows.append({"registration": reg, "position": position})

    general_position = None
    total_points = None
    for item in general_ranking():
        if item["user"].pk == user.pk:
            general_position = item["position"]
            total_points = item["total_points"]
            break

    return {"rows": rows, "total_points": total_points, "general_position": general_position}