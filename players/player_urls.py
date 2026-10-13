from django.urls import path

from . import views

urlpatterns = [
    path("", views.MyProfileView.as_view(), name="my_profile"),
    path("inscribirme/", views.MyRegistrationCreateView.as_view(), name="my_registration_create"),
    path("inscripcion/<int:pk>/cancelar/", views.MyRegistrationDeleteView.as_view(), name="my_registration_delete"),
]