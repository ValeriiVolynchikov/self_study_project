from django.core.management import BaseCommand

from authentication.models import User


class Command(BaseCommand):
    """Команда для создания администратора"""

    help = "Создание суперпользователя при необходимости"

    def handle(self, *args, **kwargs):
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                email="admin@example.com",
                password="admin",
                role="admin",
            )
            self.stdout.write(self.style.SUCCESS("Суперпользователь создан"))
        else:
            self.stdout.write("Суперпользователь уже существует")
