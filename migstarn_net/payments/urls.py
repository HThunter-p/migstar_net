from django.urls import path

from .views import daraja_callback


urlpatterns = [
    path(
        "daraja/callback/",
        daraja_callback,
        name="daraja-callback",
    ),
]