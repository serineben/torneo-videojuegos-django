import random

from django.core.management.base import BaseCommand

from accounts.models import User
from games.models import Game
from players.models import Registration

GAMES = [
    ("FIFA 24", "Simulador de fútbol."),
    ("Mario Kart 8", "Carreras de karts."),
    ("Rocket League", "Fútbol con coches."),
    ("Tetris", "Clásico juego de puzles."),
    ("Street Fighter 6", "Juego de lucha."),
]

# Point range per level, so experts tend to score higher
POINTS_RANGE = {
    Registration.Level.AMATEUR: (0, 60),
    Registration.Level.NORMAL: (20, 80),
    Registration.Level.EXPERT: (40, 100),
}


class Command(BaseCommand):
    help = "Create demo games, participants, registrations and points."

    def add_arguments(self, parser):
        parser.add_argument("--players", type=int, default=20, help="Number of demo players")
        parser.add_argument("--clear", action="store_true", help="Delete previous demo players first")

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = User.objects.filter(username__startswith="demo_").delete()
            self.stdout.write(f"Eliminados {deleted} objetos de demo anteriores.")

        games = []
        for name, description in GAMES:
            game, _ = Game.objects.get_or_create(name=name, defaults={"description": description})
            games.append(game)

        levels = list(Registration.Level)
        created_players = 0
        created_regs = 0

        for i in range(1, options["players"] + 1):
            user, created = User.objects.get_or_create(
                username=f"demo_{i:02d}",
                defaults={"email": f"demo_{i:02d}@example.com", "role": User.Role.PLAYER},
            )
            if created:
                user.set_password("demo1234")
                user.save()
                created_players += 1

            # Each player joins 1 to 3 random games
            for game in random.sample(games, k=random.randint(1, 3)):
                level = random.choice(levels)
                low, high = POINTS_RANGE[level]
                # ~20% of registrations have no result yet
                points = None if random.random() < 0.2 else random.randint(low, high)
                _, reg_created = Registration.objects.get_or_create(
                    user=user, game=game, defaults={"level": level, "points": points}
                )
                created_regs += int(reg_created)

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {created_players} participantes y {created_regs} inscripciones creados."
        ))