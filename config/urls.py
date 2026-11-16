"""Маршруты всего проекта. reviews.urls содержит маршруты приложения задач."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("reviews.urls")),
    path("reviews/", include("reviews.urls")),
]
