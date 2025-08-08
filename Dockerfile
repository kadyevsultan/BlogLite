# Используем официальный python-образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY req.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r req.txt

# Копируем код проекта
COPY . .

# Собираем статические файлы (если используешь collectstatic)
# RUN python manage.py collectstatic --noinput

# Открываем порт (если нужно)
EXPOSE 8000

# Команда запуска (можешь заменить на gunicorn, если надо)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]