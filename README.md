BlogLite
REST API блог-платформы на Django + DRF с поддержкой вложенных постов (SubPost), лайков, просмотров и Docker-контейнеризацией.

🚀 Быстрый старт
Клонирование репозитория
git clone https://github.com/kadyevsultan/bloglite.git
cd bloglite

Запуск через Docker Compose
docker-compose up --build
Приложение будет доступно по адресу: http://localhost:8000/

База данных и миграции применяются автоматически (если настроено)

⚙️ Основные команды
Запуск тестов внутри контейнера

docker-compose run app pytest
Запуск тестов с покрытием кода

docker-compose run app pytest --cov=blog --cov-report=term-missing

📦 API эндпоинты
/api/posts/ — CRUD постов с вложенными subposts

/api/subposts/ — CRUD вложенных постов (SubPost)

/api/posts/{id}/like/ — поставить/убрать лайк

/api/posts/{id}/views-count/ — увеличить счётчик просмотров

🧩 Стек технологий
Python 3.12

Django 5.2

Django REST Framework

PostgreSQL (в контейнере)

Docker & Docker Compose


