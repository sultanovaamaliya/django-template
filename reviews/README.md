# Список задач и Гостевая книга (Отзывы) на Django

Учебный проект по курсу «Python и Web». Включает два приложения:
1. **Список задач (`tasks`)** — добавление задач, переключение статуса, просмотр отдельной задачи, удаление, работа с JSON API и админкой через модель `Task`.
2. **Гостевая книга (`reviews`)** — публикация и просмотр отзывов с проверкой полей на сервере и поиском по автору в админке через модель `Review`.

На примере проекта реализованы устройство приложений Django, ORM, миграции, Django Template Language, `ModelForm`, защита CSRF и тестирование с `pytest-django`.

## Как запустить

Нужен Python 3.10 или новее. Откройте терминал в папке проекта, рядом с `manage.py`. Зависимости проекта используют Django 5.2.

**macOS и Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py makemigrations tasks reviews
python manage.py migrate
python manage.py runserver
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py makemigrations tasks reviews
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Команда `makemigrations tasks reviews` создаёт файлы миграций в `tasks/migrations/` и `reviews/migrations/`, а `migrate` создаёт таблицы в базе данных `db.sqlite3`. Повторный запуск `migrate` и перезапуск сервера сохраняют существующие записи.

После запуска сервера доступны страницы:
- [Список задач](http://127.0.0.1:8000/tasks/)
- [Отзывы (Гостевая книга)](http://127.0.0.1:8000/reviews/)

Остановка сервера — `Ctrl+C`.

## Что попробовать

### 1. Приложение «Отзывы» (`reviews`)
1. Откройте [страницу отзывов](http://127.0.0.1:8000/reviews/), добавьте отзыв с именем автора и текстом.
2. Перезапустите сервер (`Ctrl+C` и повторный `runserver`) и обновите страницу — отзывы сохраняются в SQLite, а обновление страницы (F5) не отправляет форму повторно благодаря перенаправлению `302`.
3. Попробуйте отправить пустые поля или строки только из пробелов — серверная валидация `ReviewForm` отклонит ввод и вернёт статус `400`.

### 2. Приложение «Список задач» (`tasks`)
1. Добавьте несколько задач на [странице задач](http://127.0.0.1:8000/tasks/), отметьте одну выполненной или удалите её кнопкой «Удалить».
2. Откройте страницу отдельной задачи по адресу `http://127.0.0.1:8000/tasks/1/`. Для несуществующего ID (например, `/tasks/9999/`) сервер вернёт `404`.
3. Откройте [список в JSON](http://127.0.0.1:8000/api/tasks/) и [выполненные задачи](http://127.0.0.1:8000/api/tasks/?done=1).

## Админка

Остановите сервер или откройте ещё один терминал с тем же виртуальным окружением и создайте суперпользователя:

```bash
python manage.py createsuperuser
```

В PowerShell используйте `.\.venv\Scripts\python.exe` вместо `python`.

Запустите сервер и войдите в [админку](http://127.0.0.1:8000/admin/):
- В разделе **Задачи (`Tasks`)** доступны поиск по названию, фильтрация и быстрое изменение статуса выполнения.
- В разделе **Отзывы (`Reviews`)** настроен поиск отзывов по имени автора (`search_fields = ("author",)`).

## Маршруты и ответы

Слеш в конце — часть маршрута. Используйте адреса в указанном виде, особенно для POST.

| Запрос | Что делает | Ответ |
| --- | --- | --- |
| `GET /` | Перенаправляет на список задач | `302` |
| `GET /tasks/` | Показывает HTML-страницу с формой и задачами | `200` |
| `POST /tasks/` | Создаёт задачу из поля формы `title` | `302` на `/tasks/`; при ошибке — `400` |
| `GET /tasks/<task_id>/` | Показывает отдельную страницу задачи с названием и состоянием | `200`; неизвестный ID — `404` |
| `POST /tasks/<task_id>/toggle/` | Переключает признак выполнения задачи | `302` на `/tasks/`; неизвестный ID — `404` |
| `POST /tasks/<task_id>/delete/` | Удаляет задачу (GET-запрос запись не удаляет) | `302` на `/tasks/`; неизвестный ID — `404` |
| `GET /api/tasks/` | Возвращает задачи в JSON (поддерживает `?done=0` и `?done=1`) | `200`; неверный фильтр — `400` |
| `GET /reviews/` | Показывает HTML-страницу с формой и списком отзывов | `200` |
| `POST /reviews/` | Создаёт новый отзыв из полей `author` и `text` | `302` на `/reviews/`; при ошибке — `400` |
| `GET /admin/` | Открывает админ-панель Django | Страница админки или переход на вход |

Во всех POST-формах используется `{% csrf_token %}`.

## Как устроен проект

| Файл | Назначение |
| --- | --- |
| [manage.py](manage.py) | Запуск сервера, миграций и других команд проекта |
| [config/settings.py](config/settings.py) | Настройки проекта, регистрация приложений `tasks` и `reviews` |
| [config/urls.py](config/urls.py) | Корневые маршруты проекта (`admin/`, `tasks.urls`, `reviews.urls`) |
| [tasks/models.py](tasks/models.py) | Модель `Task`: название, статус выполнения и дата создания |
| [tasks/forms.py](tasks/forms.py) | `TaskForm`: проверка и очистка названия задачи |
| [tasks/views.py](tasks/views.py) | Представления списка, создания, просмотра, переключения, удаления и JSON API |
| [tasks/urls.py](tasks/urls.py) | Маршруты приложения задач |
| [tasks/admin.py](tasks/admin.py) | Настройка модели `Task` в админке |
| [tasks/templates/tasks/](tasks/templates/tasks/) | HTML-шаблоны `task_list.html` и `task_detail.html` |
| [reviews/models.py](reviews/models.py) | Модель `Review`: имя автора, текст отзыва и время создания |
| [reviews/forms.py](reviews/forms.py) | `ReviewForm`: серверная проверка обоих полей, отклонение пустых строк и пробелов |
| [reviews/views.py](reviews/views.py) | Вывод отзывов через ORM и обработка POST-формы с редиректом |
| [reviews/urls.py](reviews/urls.py) | Маршруты приложения отзывов |
| [reviews/admin.py](reviews/admin.py) | Регистрация модели `Review` в админке и поиск по автору |
| [reviews/migrations/](reviews/migrations/) | Миграции базы данных для приложения отзывов |
| [reviews/templates/reviews/review_list.html](reviews/templates/reviews/review_list.html) | Шаблон страницы гостевой книги |
| [tests/](tests/) | Автоматические тесты для приложений `tasks` и `reviews` |

## Как запустить тесты

Установите зависимости для разработки и запустите `pytest` из корня проекта:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

Тесты проверяют:
- Отображение, создание, валидацию и переключение задач;
- Получение страницы отдельной задачи и возврат `404` для неизвестного ID;
- Исчезновение задачи после `POST` на удаление и запрет удаления через `GET`;
- Создание отзыва в приложении `reviews`, редирект и отклонение пустых строк / строк из пробелов;
- Работу JSON API, защиту CSRF и права доступа к админке.

## Если запуск не получился

- `No module named django` — проверьте активацию виртуального окружения и установите `requirements.txt`.
- `no such table` — выполните `python manage.py makemigrations tasks reviews`, затем `python manage.py migrate`.
- `403 CSRF verification failed` — проверьте наличие `{% csrf_token %}` внутри формы и обновите страницу.
- Порт 8000 занят — запустите `python manage.py runserver 8001` и откройте сайт на порту 8001.
