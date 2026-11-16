from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.index, name="index"),
    path("reviews/", views.task_list, name="task_list"),
    path("reviews/<int:task_id>/toggle/", views.task_toggle, name="task_toggle"),
    path("api/reviews/", views.task_api, name="task_api"),
    path("reviews/<int:task_id>/", views.task_detail, name="task_detail"),
    path("reviews/<int:task_id>/delete/", views.task_delete, name="task_delete"),
]
