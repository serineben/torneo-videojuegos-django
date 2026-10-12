from django.urls import path
from .views import GameCreateView, GameDeleteView, GameListView, GameUpdateView

urlpatterns = [
    path("", GameListView.as_view(), name="game_list"),
    path("nuevo/", GameCreateView.as_view(), name="game_create"),
    path("<int:pk>/editar/", GameUpdateView.as_view(), name="game_update"),
    path("<int:pk>/eliminar/", GameDeleteView.as_view(), name="game_delete"),
]