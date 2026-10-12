from django.db import models


class Game(models.Model):
    name = models.CharField("Nombre", max_length=100, unique=True)
    description = models.TextField("Descripción", blank=True)
    image = models.ImageField("Imagen", upload_to="games/", blank=True, null=True)
    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)

    class Meta:
        verbose_name = "Juego"
        verbose_name_plural = "Juegos"
        ordering = ["name"]

    def __str__(self):
        return self.name