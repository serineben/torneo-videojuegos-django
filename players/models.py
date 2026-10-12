from django.conf import settings
from django.db import models

from games.models import Game


class Registration(models.Model):
    class Level(models.TextChoices):
        AMATEUR = "amateur", "Amateur"
        NORMAL = "normal", "Normal"
        EXPERT = "expert", "Expert"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Participante",
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Juego",
    )
    level = models.CharField("Nivel", max_length=10, choices=Level.choices, default=Level.NORMAL)
    points = models.PositiveIntegerField("Puntos", null=True, blank=True)
    created_at = models.DateTimeField("Fecha de inscripción", auto_now_add=True)

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        constraints = [
            models.UniqueConstraint(fields=["user", "game"], name="unique_user_game"),
        ]
        ordering = ["game__name", "-points"]

    def __str__(self):
        return f"{self.user} - {self.game} ({self.get_level_display()})"