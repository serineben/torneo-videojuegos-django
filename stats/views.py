from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from games.models import Game
from . import services
from players.services import general_ranking


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "stats/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        games = Game.objects.all()

        # Selected game for the per-game chart (?game=<id>), default: first game
        selected = None
        try:
            selected = games.filter(pk=int(self.request.GET.get("game", ""))).first()
        except ValueError:
            pass
        selected = selected or games.first()

        context.update({
            "summary": services.summary(),
            "top_players": services.top_players(),
            "level_distribution": services.level_distribution(),
            "registrations_per_game": services.registrations_per_game(),
            "average_points": services.average_points_per_game(),
            "games": games,
            "selected_game": selected,
            "game_points": services.points_for_game(selected) if selected else None,
        })
        return context

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["summary"] = services.summary()
        context["games"] = Game.objects.all()[:6]
        # The podium is only shown to logged-in users, like the dashboard
        if self.request.user.is_authenticated:
            context["podium"] = general_ranking()[:3]
        return context