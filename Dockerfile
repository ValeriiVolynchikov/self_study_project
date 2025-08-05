# Базовый образ Python
FROM python:3.12-slim

# Установка системных зависимостей
# Для деплоя на сервер убрать комментарии
RUN apt-get update && apt-get install -y \
   build-essential \
   libpq-dev \
   && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Команда запуска (будет переопределена в docker-compose при необходимости)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]