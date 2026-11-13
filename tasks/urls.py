from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.index, name="index"),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/<int:task_id>/toggle/", views.task_toggle, name="task_toggle"),
    path("api/tasks/", views.task_api, name="task_api"),
    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
]
