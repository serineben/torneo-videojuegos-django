from django.contrib.auth.mixins import UserPassesTestMixin


class AdminRequiredMixin(UserPassesTestMixin):
    """Only authenticated users with the admin role can access the view."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_role

class PlayerRequiredMixin(UserPassesTestMixin):
    """Only authenticated users with the player role can access the view."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role == user.Role.PLAYER


class QueryStringMixin:
    """Adds the current GET parameters (without 'page') to the context, to keep filters when paginating."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context["query_string"] = params.urlencode()
        return context