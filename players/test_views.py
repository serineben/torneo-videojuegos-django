from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from config.testing import make_admin, make_game, make_registration, make_user
from players.models import Registration


class ParticipantListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.game_a = make_game("Game A")
        cls.game_b = make_game("Game B")
        cls.alice = make_user("alice")
        cls.bob = make_user("bob")
        make_registration(cls.alice, cls.game_a, Registration.Level.EXPERT)
        make_registration(cls.alice, cls.game_b, Registration.Level.AMATEUR)
        make_registration(cls.bob, cls.game_b, Registration.Level.EXPERT)

    def setUp(self):
        self.client.force_login(self.admin)
        self.url = reverse("participant_list")

    def usernames(self, **params):
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        return sorted(p.username for p in response.context["participants"])

    def test_lists_players_once_and_excludes_admins(self):
        self.assertEqual(self.usernames(), ["alice", "bob"])

    def test_search_by_name(self):
        self.assertEqual(self.usernames(q="ali"), ["alice"])

    def test_search_by_email(self):
        self.assertEqual(self.usernames(q="bob@example"), ["bob"])

    def test_filter_by_game(self):
        self.assertEqual(self.usernames(game=self.game_a.pk), ["alice"])
        self.assertEqual(self.usernames(game=self.game_b.pk), ["alice", "bob"])

    def test_filter_by_level(self):
        self.assertEqual(self.usernames(level="expert"), ["alice", "bob"])
        self.assertEqual(self.usernames(level="amateur"), ["alice"])

    def test_game_and_level_apply_to_the_same_registration(self):
        # alice is EXPERT in Game A and AMATEUR in Game B
        self.assertEqual(self.usernames(game=self.game_a.pk, level="amateur"), [])
        self.assertEqual(self.usernames(game=self.game_b.pk, level="amateur"), ["alice"])

    def test_invalid_level_is_ignored(self):
        self.assertEqual(self.usernames(level="hacker"), ["alice", "bob"])

    def test_pagination_keeps_filters(self):
        for i in range(12):
            make_user(f"extra{i:02d}")
        response = self.client.get(self.url, {"q": "extra", "page": 2})
        self.assertEqual(len(response.context["participants"]), 2)
        self.assertEqual(response.context["query_string"], "q=extra")
        first_page = self.client.get(self.url, {"q": "extra"})
        self.assertEqual(len(first_page.context["participants"]), 10)


class ParticipantCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()

    def setUp(self):
        self.client.force_login(self.admin)

    def test_create_participant_is_always_player(self):
        data = {
            "username": "newbie",
            "email": "newbie@example.com",
            "password1": "Str0ngPass!2024",
            "password2": "Str0ngPass!2024",
            "role": "admin",
        }
        response = self.client.post(reverse("participant_create"), data)
        self.assertRedirects(response, reverse("participant_list"))
        self.assertEqual(User.objects.get(username="newbie").role, User.Role.PLAYER)

    def test_update_participant(self):
        user = make_user("alice")
        data = {"username": "alice2", "email": "alice@example.com"}  # is_active omitted = False
        self.client.post(reverse("participant_update", args=[user.pk]), data)
        user.refresh_from_db()
        self.assertEqual(user.username, "alice2")
        self.assertFalse(user.is_active)

    def test_delete_participant_removes_registrations(self):
        user = make_user("alice")
        make_registration(user, make_game())
        self.client.post(reverse("participant_delete", args=[user.pk]))
        self.assertFalse(User.objects.filter(pk=user.pk).exists())
        self.assertEqual(Registration.objects.count(), 0)

    def test_admin_is_not_reachable_as_participant(self):
        response = self.client.get(reverse("participant_detail", args=[self.admin.pk]))
        self.assertEqual(response.status_code, 404)


class AdminRegistrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.alice = make_user("alice")
        cls.game = make_game("Pong")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_create_registration(self):
        url = reverse("registration_create", args=[self.alice.pk])
        response = self.client.post(url, {"game": self.game.pk, "level": "expert"})
        self.assertRedirects(response, reverse("participant_detail", args=[self.alice.pk]))
        reg = Registration.objects.get(user=self.alice, game=self.game)
        self.assertEqual(reg.level, "expert")

    def test_duplicate_registration_is_rejected(self):
        make_registration(self.alice, self.game)
        url = reverse("registration_create", args=[self.alice.pk])
        response = self.client.post(url, {"game": self.game.pk, "level": "normal"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ya está inscrito")
        self.assertEqual(Registration.objects.count(), 1)

    def test_update_registration_level(self):
        reg = make_registration(self.alice, self.game)
        url = reverse("registration_update", args=[reg.pk])
        self.client.post(url, {"game": self.game.pk, "level": "amateur"})
        reg.refresh_from_db()
        self.assertEqual(reg.level, "amateur")

    def test_delete_registration(self):
        reg = make_registration(self.alice, self.game)
        self.client.post(reverse("registration_delete", args=[reg.pk]))
        self.assertFalse(Registration.objects.filter(pk=reg.pk).exists())


class PointsEntryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = make_admin()
        cls.game = make_game("Pong")
        cls.r1 = make_registration(make_user("alice"), cls.game)
        cls.r2 = make_registration(make_user("bob"), cls.game)

    def setUp(self):
        self.client.force_login(self.admin)
        self.url = reverse("game_points", args=[self.game.pk])

    def formset_data(self, p1, p2):
        # Forms follow the queryset order (by username): alice, bob
        return {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 2,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
            "form-0-id": self.r1.pk,
            "form-0-points": p1,
            "form-1-id": self.r2.pk,
            "form-1-points": p2,
        }

    def test_save_points_redirects_to_ranking(self):
        response = self.client.post(self.url, self.formset_data(40, 20))
        self.assertRedirects(response, reverse("game_ranking", args=[self.game.pk]))
        self.r1.refresh_from_db()
        self.r2.refresh_from_db()
        self.assertEqual((self.r1.points, self.r2.points), (40, 20))

    def test_negative_points_are_rejected(self):
        response = self.client.post(self.url, self.formset_data(-5, 20))
        self.assertEqual(response.status_code, 200)
        self.r1.refresh_from_db()
        self.assertIsNone(self.r1.points)

    def test_ranking_pages_show_results(self):
        self.client.post(self.url, self.formset_data(40, 20))
        game_page = self.client.get(reverse("game_ranking", args=[self.game.pk]))
        self.assertEqual(game_page.context["ranking"][0]["registration"].user.username, "alice")
        general_page = self.client.get(reverse("general_ranking"))
        self.assertEqual(general_page.context["ranking"][0]["total_points"], 40)