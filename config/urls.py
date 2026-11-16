"""Маршруты всего проекта. tasks.urls содержит маршруты приложения задач."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tasks.urls")),
    path(" reviews/", include("reviews.urls")),
]
