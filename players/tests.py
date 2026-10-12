from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from games.models import Game
from .models import Registration


User = get_user_model()


class RegistrationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="player",
            email="player@example.com",
            password="test-password",
        )
        self.game = Game.objects.create(name="Chess")

    def test_user_cannot_register_twice_for_same_game(self):
        Registration.objects.create(user=self.user, game=self.game)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Registration.objects.create(user=self.user, game=self.game)

    def test_amateur_normal_and_expert_are_valid_levels(self):
        valid_levels = {"amateur", "normal", "expert"}
        choices = {value for value, _label in Registration.Level.choices}

        self.assertEqual(choices, valid_levels)
        for level in valid_levels:
            with self.subTest(level=level):
                registration = Registration(
                    user=self.user,
                    game=self.game,
                    level=level,
                )
                registration.full_clean()

    def test_unknown_level_is_invalid(self):
        registration = Registration(
            user=self.user,
            game=self.game,
            level="beginner",
        )

        with self.assertRaises(ValidationError):
            registration.full_clean()


class ParticipantListPermissionTests(TestCase):
    def test_player_receives_forbidden_response(self):
        player = User.objects.create_user(
            username="player",
            email="player@example.com",
            password="test-password",
            role=User.Role.PLAYER,
        )
        self.client.force_login(player)

        response = self.client.get(reverse("participant_list"))

        self.assertEqual(response.status_code, 403)
