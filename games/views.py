from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.mixins import AdminRequiredMixin
from .forms import GameForm
from .models import Game


class GameListView(AdminRequiredMixin, ListView):
    model = Game
    template_name = "games/game_list.html"
    context_object_name = "games"


class GameCreateView(AdminRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = "games/game_form.html"
    success_url = reverse_lazy("game_list")

    def form_valid(self, form):
        messages.success(self.request, "Juego creado correctamente.")
        return super().form_valid(form)


class GameUpdateView(AdminRequiredMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = "games/game_form.html"
    success_url = reverse_lazy("game_list")

    def form_valid(self, form):
        messages.success(self.request, "Juego actualizado correctamente.")
        return super().form_valid(form)


class GameDeleteView(AdminRequiredMixin, DeleteView):
    model = Game
    template_name = "games/game_confirm_delete.html"
    success_url = reverse_lazy("game_list")

    def form_valid(self, form):
        messages.success(self.request, "Juego eliminado correctamente.")
        return super().form_valid(form)