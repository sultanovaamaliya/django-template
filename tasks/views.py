"""Django передаёт HttpRequest аргументом в функцию представления.

URL-конфигурация выбирает функцию. ORM обращается к SQLite через модель,
а render() передаёт данные в Django Template Language и возвращает HTML.
"""

from django.db.models import F
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import TaskForm
from .models import Task


@require_GET
def index(request):
    return redirect("tasks:task_list")


@require_http_methods(["GET", "POST"])
def task_list(request):
    status = 200
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            # Стандартный redirect Django вернёт 302. Браузер выполнит GET.
            return redirect("tasks:task_list")
        status = 400
    else:
        form = TaskForm()

    return render(
        request,
        "tasks/task_list.html",
        {"tasks": Task.objects.all(), "form": form},
        status=status,
    )

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, "tasks/task_detail.html", {"task": task})

def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.delete()

    return redirect("tasks:task_list")

@require_POST
def task_toggle(request, task_id):
    # F обращается к значению в БД. Переключение выполняется одним UPDATE.
    updated = Task.objects.filter(pk=task_id).update(done=~F("done"))
    if updated == 0:
        raise Http404("Задача не найдена.")
    return redirect("tasks:task_list")


@require_GET
def task_api(request):
    done = request.GET.get("done")
    if done not in (None, "0", "1"):
        return JsonResponse({"error": "Параметр done должен быть 0 или 1."}, status=400)

    tasks = Task.objects.all()
    if done is not None:
        tasks = tasks.filter(done=done == "1")
    return JsonResponse({"tasks": list(tasks.values("id", "title", "done"))})
