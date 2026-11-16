# Список задач на Django

Учебный проект для второй пары «Python и Web». Добавьте задачу через HTML-форму, отметьте её выполненной и найдите ту же запись в админке. Страница, админка и JSON API работают с одной базой SQLite через модель `Task`.

На примере разбираем устройство проекта Django, ORM, миграции, Django Template Language, `ModelForm`, CSRF и тестирование с `pytest-django`.

## Как запустить

Нужен Python 3.10 или новее. Откройте терминал в папке `django-template`, рядом с `manage.py`. Зависимости проекта используют Django 5.2.

**macOS и Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py makemigrations reviews
python manage.py migrate
python manage.py runserver
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py makemigrations tasks
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

В этом шаблоне начальную миграцию приложения `tasks` создаём самостоятельно. Команда `makemigrations tasks` записывает описание таблицы в `tasks/migrations/`, а `migrate` создаёт таблицы задач и встроенных приложений Django в файле `db.sqlite3`. Повторный `migrate` сохраняет существующие записи.

Откройте [список задач](http://127.0.0.1:8000/tasks/). Остановка сервера — `Ctrl+C`. При следующем запуске на macOS и Linux активируйте окружение и выполните `python manage.py runserver`; в PowerShell используйте последнюю команду из своего блока. Команды `startproject` и `startapp` для скачанного шаблона не нужны.

## Что попробовать

1. Добавьте несколько задач, отметьте одну выполненной и перезапустите сервер. Проверьте, что записи сохранились.
2. Откройте [список в JSON](http://127.0.0.1:8000/api/tasks/) и [выполненные задачи](http://127.0.0.1:8000/api/tasks/?done=1). Найдите поля `id`, `title` и `done`.
3. Попробуйте отправить пустое название, пробелы или строку длиннее 120 символов. Форма проверяет данные на сервере и показывает ошибку. В проверке длины учитывается строка после удаления пробелов по краям.

В браузере нажмите правой кнопкой по странице и выберите «Исследовать» или «Просмотреть код». Перейдите на вкладку **Network / Сеть**, включите **Preserve log / Сохранять журнал** и добавьте задачу.

- В **Payload** запроса `POST /tasks/` найдите `title` и `csrfmiddlewaretoken`.
- В **Headers** проверьте статус `302` и заголовок `Location: /tasks/`.
- Следующий `GET /tasks/` загружает обновлённый список. Обновление страницы после перехода не добавляет задачу повторно.

## Админка

Остановите сервер или откройте ещё один терминал с тем же виртуальным окружением и создайте пользователя:

```bash
python manage.py createsuperuser
```

В PowerShell здесь и далее используйте `.\.venv\Scripts\python.exe` вместо `python`.

Запустите сервер и войдите в [админку](http://127.0.0.1:8000/admin/). Откройте раздел «Задачи»: добавьте запись, найдите её по части названия, примените фильтр и измените признак выполнения прямо в списке. Затем проверьте изменения на обычной странице.

Настройки этих возможностей находятся в [tasks/admin.py](tasks/admin.py): `list_display`, `search_fields`, `list_filter` и `list_editable`. Для входа в админку нужна учётная запись с правом доступа; обычная страница задач доступна без входа.

## Маршруты и ответы

Слеш в конце — часть маршрута. Используйте адреса в указанном виде, особенно для POST.

| Запрос | Что делает | Ответ |
| --- | --- | --- |
| `GET /` | Перенаправляет на список задач | `302` |
| `GET /tasks/` | Показывает HTML-страницу с формой и задачами, новые сверху | `200` |
| `POST /tasks/` | Создаёт задачу из поля формы `title` | `302` на `/tasks/`; при ошибке ввода — HTML с ошибками и `400` |
| `POST /tasks/<task_id>/toggle/` | Переключает признак выполнения | `302` на `/tasks/`; неизвестный ID — `404` |
| `GET /api/tasks/` | Возвращает задачи в JSON | `200` |
| `GET /api/tasks/?done=0` | Возвращает невыполненные задачи | `200` |
| `GET /api/tasks/?done=1` | Возвращает выполненные задачи | `200` |
| `GET /admin/` | Открывает админку | Страница админки или переход на вход |

JSON API в этом примере поддерживает чтение. Создание и переключение задач выполняются HTML-формами. Неподдерживаемый метод для маршрутов приложения задач возвращает `405`; проверка CSRF может отклонить небезопасный запрос раньше, со статусом `403`. Неверное значение `done`, например `?done=yes`, даёт JSON с ошибкой и статус `400`.

Пример ответа API:

```json
{
  "tasks": [
    {"id": 1, "title": "Разобраться с Django", "done": false}
  ]
}
```

## Как устроен проект

| Файл | Назначение |
| --- | --- |
| [manage.py](manage.py) | Запуск сервера, миграций и других команд проекта |
| [config/settings.py](config/settings.py) | Подключённые приложения, SQLite, шаблоны и middleware |
| [config/urls.py](config/urls.py) | Общие маршруты проекта и подключение `tasks.urls` |
| [tasks/urls.py](tasks/urls.py) | Связь адресов с функциями представлений |
| [tasks/views.py](tasks/views.py) | Обработка GET и POST, работа с формой, HTML- и JSON-ответы |
| [tasks/models.py](tasks/models.py) | Модель `Task`: название, признак выполнения и время создания |
| [tasks/forms.py](tasks/forms.py) | `TaskForm`: поля и ограничения из модели, проверка ввода, сохранение |
| [tasks/migrations/](tasks/migrations/) | История изменений схемы базы данных |
| [tasks/admin.py](tasks/admin.py) | Регистрация и настройка модели в админке |
| [tasks/templates/tasks/task_list.html](tasks/templates/tasks/task_list.html) | Шаблон страницы на Django Template Language |
| [tasks/static/tasks/style.css](tasks/static/tasks/style.css) | Стили страницы |
| [tests/test_tasks.py](tests/test_tasks.py) | Тесты запросов, формы, базы данных, CSRF и админки |

`config` содержит настройки всего проекта, а `tasks` — отдельное приложение. В одном проекте могут быть несколько приложений.

Путь запроса: браузер → URL-конфигурация → функция в `views.py` → ORM и форма → шаблон → HTTP-ответ. Представление получает объект `request` аргументом. `request.GET` содержит параметры URL, `request.POST` — поля отправленной формы.

Шаблон использует **Django Template Language**: `{{ task.title }}` выводит значение, `{% for %}` перебирает записи, `{% url %}` строит адрес по имени маршрута. Пользовательский текст экранируется при выводе.

В каждой POST-форме есть `{% csrf_token %}`. Middleware проверяет токен и при провале проверки возвращает `403`. Проверка CSRF и проверка содержимого `title` решают разные задачи: корректный токен не делает название допустимым.

## ORM и миграции на практике

После первого запуска откройте Django shell:

```bash
python manage.py shell
```

Выполните команды по очереди:

```python
from tasks.models import Task

task = Task.objects.create(title="Изучить ORM")
Task.objects.all()
Task.objects.filter(done=False)
Task.objects.get(pk=task.pk)

task.done = True
task.save(update_fields=["done"])
Task.objects.values("id", "title", "done")

task.delete()
```

`create()` сразу сохраняет запись. Присваивание `task.done = True` изменяет Python-объект; вызов `save()` записывает изменение в базу. `get()` ожидает одну запись и при её отсутствии вызывает `Task.DoesNotExist`.

Для эксперимента добавьте в класс `Task` новое поле:

```python
priority = models.PositiveSmallIntegerField(default=0)
```

Затем в терминале выполните:

```bash
python manage.py makemigrations reviews
python manage.py migrate
python manage.py showmigrations reviews
```

Перезапустите Django shell и проверьте `Task.objects.values("title", "priority")`. У существующих записей появится значение `0`. Изменения модели оформляйте миграциями и сохраняйте файлы миграций вместе с исходным кодом.

## Как запустить тесты

После создания начальной миграции установите зависимости для разработки и запустите pytest из папки с `manage.py`:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

`pytest-django` берёт настройки из [pytest.ini](pytest.ini) и создаёт отдельную тестовую базу. Рабочие задачи из `db.sqlite3` не используются. Фикстура `client` вызывает приложение без запуска сервера; `@pytest.mark.django_db` разрешает тесту обращаться к базе.

Обычный тестовый клиент отключает проверку CSRF. В отдельном тесте она включена через `Client(enforce_csrf_checks=True)`: проверяются отказ без токена и успешная отправка с токеном.

## Самостоятельная работа

1. Добавьте `GET /tasks/<int:task_id>/`: отдельную HTML-страницу с названием и состоянием задачи. Для неизвестного ID верните `404`.
2. Добавьте `POST /tasks/<int:task_id>/delete/` и кнопку удаления в форме с CSRF-токеном. После удаления перенаправляйте на список; для неизвестного ID верните `404`. GET не должен удалять запись.
3. Добавьте тесты: получение нужной задачи, `404` для неизвестной, исчезновение записи после удаления и запрет удаления через GET.

Подсказки: `path()`, `get_object_or_404(Task, pk=task_id)`, `render()`, `@require_POST`, `task.delete()`, `redirect("tasks:task_list")` и `{% csrf_token %}`. В отдельном шаблоне можно использовать имя маршрута для ссылки обратно на список.

Дополнительно — фильтр «Все / В работе / Выполнены» на HTML-странице. Посмотрите, как `task_api()` получает `done` из `request.GET` и применяет `filter()`.

## Домашнее задание. Гостевая книга

Сделайте собственное приложение на Django по образцу списка задач.

- Опишите модель `Review` с именем автора и текстом отзыва. Создайте и примените миграцию.
- Покажите отзывы на странице через ORM и шаблон.
- Добавьте `ModelForm` с проверкой обоих полей на сервере. Пустые строки и строки из пробелов отклоняйте. В POST-форму включите CSRF-токен.
- После успешного POST перенаправляйте на список отзывов. Обновление страницы не должно добавлять отзыв повторно.
- Зарегистрируйте модель в админке, настройте поиск по автору.
- Проверьте сохранение данных после перезапуска. Добавьте тесты создания отзыва и отклонения неверного ввода.
- Подготовьте README с командами установки, миграций и запуска. Сдайте исходники вместе с миграциями.

Дополнительно — модерация через поле `is_published`: новые отзывы скрыты, преподаватель или модератор публикует их в админке, на странице видны только опубликованные.

## Если запуск не получился

- `No module named django` — проверьте выбранное виртуальное окружение и установите `requirements.txt` тем же интерпретатором.
- `no such table: tasks_task` — выполните `python manage.py makemigrations tasks`, затем `python manage.py migrate`.
- Предупреждение о неприменённых миграциях — выполните `python manage.py migrate`.
- `403 CSRF verification failed` — проверьте наличие `{% csrf_token %}` внутри формы и загрузите страницу заново. Используйте один адрес, например `127.0.0.1`, на протяжении работы с формой.
- Порт 8000 занят — запустите `python manage.py runserver 8001` и откройте страницу на порту 8001.

## Материалы

- [Официальный учебник Django 5.2](https://docs.djangoproject.com/en/5.2/intro/tutorial01/)
- [Запросы через ORM](https://docs.djangoproject.com/en/5.2/topics/db/queries/)
- [Миграции](https://docs.djangoproject.com/en/5.2/topics/migrations/)
- [ModelForm](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/)
- [CSRF](https://docs.djangoproject.com/en/5.2/ref/csrf/)
- [pytest-django](https://pytest-django.readthedocs.io/en/latest/)
