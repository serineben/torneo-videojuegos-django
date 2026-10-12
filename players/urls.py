from django.urls import path
from . import views

urlpatterns = [
    path("", views.ParticipantListView.as_view(), name="participant_list"),
    path("nuevo/", views.ParticipantCreateView.as_view(), name="participant_create"),
    path("<int:pk>/", views.ParticipantDetailView.as_view(), name="participant_detail"),
    path("<int:pk>/editar/", views.ParticipantUpdateView.as_view(), name="participant_update"),
    path("<int:pk>/eliminar/", views.ParticipantDeleteView.as_view(), name="participant_delete"),
    path("<int:user_pk>/inscribir/", views.RegistrationCreateView.as_view(), name="registration_create"),
    path("inscripcion/<int:pk>/editar/", views.RegistrationUpdateView.as_view(), name="registration_update"),
    path("inscripcion/<int:pk>/eliminar/", views.RegistrationDeleteView.as_view(), name="registration_delete"),
]