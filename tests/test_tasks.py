import pytest
from django.test import Client
from django.urls import reverse

from tasks.forms import TaskForm
from tasks.models import Task

pytestmark = pytest.mark.django_db


def test_list_renders_saved_tasks(client):
    Task.objects.create(title="Первая")
    Task.objects.create(title="Вторая")
    response = client.get(reverse("tasks:task_list"))
    assert response.status_code == 200
    assert [task.title for task in response.context["tasks"]] == ["Вторая", "Первая"]
    assert "Первая" in response.content.decode()


def test_form_creates_task_and_redirects(client):
    response = client.post(reverse("tasks:task_list"), {"title": "  Читать Django  "})
    assert response.status_code == 302
    assert response.url == reverse("tasks:task_list")
    task = Task.objects.get()
    assert task.title == "Читать Django"
    assert task.done is False
    assert client.get(response.url).status_code == 200
    assert Task.objects.count() == 1


@pytest.mark.parametrize("title", ["", "   ", "x" * 121])
def test_invalid_title_is_rejected(client, title):
    response = client.post(reverse("tasks:task_list"), {"title": title})
    assert response.status_code == 400
    assert "title" in response.context["form"].errors
    assert not Task.objects.exists()


def test_model_form_accepts_title_at_maximum_length():
    form = TaskForm({"title": "x" * 120})
    assert form.is_valid()
    assert len(form.save().title) == 120


def test_toggle_updates_existing_task(client):
    task = Task.objects.create(title="Проверить ORM")
    url = reverse("tasks:task_toggle", args=[task.pk])
    assert client.post(url).status_code == 302
    task.refresh_from_db()
    assert task.done is True
    assert client.post(url).status_code == 302
    task.refresh_from_db()
    assert task.done is False


def test_missing_task_returns_404(client):
    response = client.post(reverse("tasks:task_toggle", args=[999]))
    assert response.status_code == 404


def test_get_cannot_change_task(client):
    task = Task.objects.create(title="Только POST")
    response = client.get(reverse("tasks:task_toggle", args=[task.pk]))
    assert response.status_code == 405
    task.refresh_from_db()
    assert task.done is False


def test_json_api_filters_tasks(client):
    Task.objects.create(title="В работе")
    done = Task.objects.create(title="Готово", done=True)
    response = client.get(reverse("tasks:task_api"), {"done": "1"})
    assert response.status_code == 200
    assert response.json() == {"tasks": [{"id": done.pk, "title": "Готово", "done": True}]}
    assert len(client.get(reverse("tasks:task_api")).json()["tasks"]) == 2


def test_json_api_rejects_invalid_filter(client):
    response = client.get(reverse("tasks:task_api"), {"done": "invalid"})
    assert response.status_code == 400


def test_template_escapes_user_input(client):
    title = "<script>alert('test')</script>"
    Task.objects.create(title=title)
    html = client.get(reverse("tasks:task_list")).content.decode()
    assert title not in html
    assert "&lt;script&gt;" in html


def test_post_requires_csrf_token():
    client = Client(enforce_csrf_checks=True)
    url = reverse("tasks:task_list")
    assert client.post(url, {"title": "Без токена"}).status_code == 403
    assert not Task.objects.exists()

    assert client.get(url).status_code == 200
    token = client.cookies["csrftoken"].value
    response = client.post(url, {"title": "С токеном", "csrfmiddlewaretoken": token})
    assert response.status_code == 302
    assert Task.objects.get().title == "С токеном"


def test_admin_requires_login(client):
    response = client.get(reverse("admin:tasks_task_changelist"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("admin:login"))


def test_admin_displays_tasks(admin_client):
    Task.objects.create(title="Задача в админке")
    response = admin_client.get(reverse("admin:tasks_task_changelist"))
    assert response.status_code == 200
    assert "Задача в админке" in response.content.decode()


def test_task_detail_success(client):
    task = Task.objects.create(title="Купить молоко", done=False)
    url = reverse("tasks:task_detail", args=[task.id])
    response = client.get(url)

    assert response.status_code == 200
    assert "Купить молоко" in response.content.decode()


def test_unknown_task_returns_404(client):
    detail_url = reverse("tasks:task_detail", args=[9999])
    delete_url = reverse("tasks:task_delete", args=[9999])
    response_detail = client.get(detail_url)
    response_delete = client.post(delete_url)

    assert response_detail.status_code == 404
    assert response_delete.status_code == 404


def test_delete_task_via_post(client):
    task = Task.objects.create(title="Удалить меня")
    url = reverse("tasks:task_delete", args=[task.id])
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse("tasks:task_list")
    assert not Task.objects.filter(id=task.id).exists()


def test_do_not_delete_task_via_get(client):
    task = Task.objects.create(title="Задача")
    url = reverse("tasks:task_delete", args=[task.id])
    client.get(url)
    assert Task.objects.filter(id=task.id).exists()