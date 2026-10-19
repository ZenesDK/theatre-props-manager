"""Маршруты приложения props."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.props, name="props"),
    path("<int:prop_id>/", views.prop_detail, name="prop_detail"),
]
