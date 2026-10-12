from django.contrib.auth.mixins import UserPassesTestMixin


class AdminRequiredMixin(UserPassesTestMixin):
    """Only authenticated users with the admin role can access the view."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_role