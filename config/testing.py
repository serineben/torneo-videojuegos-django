from accounts.models import User
from games.models import Game
from players.models import Registration

PASSWORD = "Pass12345!"


def make_user(username="player1", role=User.Role.PLAYER):
    return User.objects.create_user(
        username=username, email=f"{username}@example.com", password=PASSWORD, role=role
    )


def make_admin(username="admin1"):
    return make_user(username, role=User.Role.ADMIN)


def make_game(name="Tetris"):
    return Game.objects.create(name=name)


def make_registration(user, game, level=Registration.Level.NORMAL, points=None):
    return Registration.objects.create(user=user, game=game, level=level, points=points)