from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.mixins import AdminRequiredMixin, QueryStringMixin

from .forms import GameForm
from .models import Game


class GameListView(AdminRequiredMixin, QueryStringMixin, ListView):
    model = Game
    template_name = "games/game_list.html"
    context_object_name = "games"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        return context

class GameDetailView(AdminRequiredMixin, DetailView):
    model = Game
    template_name = "games/game_detail.html"
    context_object_name = "game"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registrations"] = (
            self.object.registrations.select_related("user").order_by("-points", "user__username")
        )
        return context

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