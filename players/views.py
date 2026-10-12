from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, FormView

from accounts.mixins import AdminRequiredMixin
from accounts.models import User
from .forms import ParticipantCreateForm, ParticipantUpdateForm, RegistrationForm
from .models import Registration


from django.shortcuts import render
from django.views import View

from games.models import Game
from .forms import PointsFormSet
from .services import game_ranking, general_ranking


class ParticipantListView(AdminRequiredMixin, ListView):
    template_name = "players/participant_list.html"
    context_object_name = "participants"

    def get_queryset(self):
        return (
            User.objects.filter(role=User.Role.PLAYER)
            .prefetch_related("registrations__game")
            .order_by("username")
        )


class ParticipantDetailView(AdminRequiredMixin, DetailView):
    model = User
    template_name = "players/participant_detail.html"
    context_object_name = "participant"

    def get_queryset(self):
        return User.objects.filter(role=User.Role.PLAYER)


class ParticipantCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = ParticipantCreateForm
    template_name = "players/participant_form.html"
    success_url = reverse_lazy("participant_list")

    def form_valid(self, form):
        messages.success(self.request, "Participante creado correctamente.")
        return super().form_valid(form)


class ParticipantUpdateView(AdminRequiredMixin, UpdateView):
    form_class = ParticipantUpdateForm
    template_name = "players/participant_form.html"
    success_url = reverse_lazy("participant_list")

    def get_queryset(self):
        return User.objects.filter(role=User.Role.PLAYER)

    def form_valid(self, form):
        messages.success(self.request, "Participante actualizado correctamente.")
        return super().form_valid(form)


class ParticipantDeleteView(AdminRequiredMixin, DeleteView):
    template_name = "players/participant_confirm_delete.html"
    success_url = reverse_lazy("participant_list")

    def get_queryset(self):
        return User.objects.filter(role=User.Role.PLAYER)

    def form_valid(self, form):
        messages.success(self.request, "Participante eliminado correctamente.")
        return super().form_valid(form)


class RegistrationCreateView(AdminRequiredMixin, CreateView):
    model = Registration
    form_class = RegistrationForm
    template_name = "players/registration_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.participant = get_object_or_404(User, pk=kwargs["user_pk"], role=User.Role.PLAYER)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.participant
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.participant
        messages.success(self.request, "Inscripción añadida correctamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["participant"] = self.participant
        return context

    def get_success_url(self):
        return reverse("participant_detail", args=[self.participant.pk])


class RegistrationUpdateView(AdminRequiredMixin, UpdateView):
    model = Registration
    form_class = RegistrationForm
    template_name = "players/registration_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.object.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["participant"] = self.object.user
        return context

    def form_valid(self, form):
        messages.success(self.request, "Inscripción actualizada correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("participant_detail", args=[self.object.user.pk])


class RegistrationDeleteView(AdminRequiredMixin, DeleteView):
    model = Registration
    template_name = "players/registration_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Inscripción eliminada correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("participant_detail", args=[self.object.user.pk])



class GamePointsView(AdminRequiredMixin, View):
    template_name = "players/game_points.html"

    def get_game(self, pk):
        return get_object_or_404(Game, pk=pk)

    def get_queryset(self, game):
        return Registration.objects.filter(game=game).select_related("user").order_by("user__username")

    def get(self, request, pk):
        game = self.get_game(pk)
        formset = PointsFormSet(queryset=self.get_queryset(game))
        return render(request, self.template_name, {"game": game, "formset": formset})

    def post(self, request, pk):
        game = self.get_game(pk)
        formset = PointsFormSet(request.POST, queryset=self.get_queryset(game))
        if formset.is_valid():
            formset.save()
            messages.success(request, "Puntos guardados correctamente.")
            return redirect("game_ranking", pk=game.pk)
        return render(request, self.template_name, {"game": game, "formset": formset})


class GameRankingView(AdminRequiredMixin, View):
    template_name = "players/game_ranking.html"

    def get(self, request, pk):
        game = get_object_or_404(Game, pk=pk)
        return render(request, self.template_name, {"game": game, "ranking": game_ranking(game)})


class GeneralRankingView(AdminRequiredMixin, View):
    template_name = "players/general_ranking.html"

    def get(self, request):
        return render(request, self.template_name, {"ranking": general_ranking()})