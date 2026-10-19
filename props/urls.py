"""Маршруты приложения props."""

from django.urls import path

from . import views

app_name = "props"

urlpatterns = [
    path("", views.props, name="props"),
    path("<int:prop_id>/", views.prop_detail, name="prop_detail"),
]
