from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {"null": True, "blank": True}


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с ролями"""

    class Role(models.TextChoices):
        TEACHER = "teacher", "Преподаватель"
        STUDENT = "student", "Студент"
        ADMIN = "admin", "Администратор"

    username = None
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.STUDENT, verbose_name="Роль"
    )
    email = models.EmailField(
        unique=True, verbose_name="Email", help_text="Введите почту"
    )
    city = models.CharField(
        max_length=40, verbose_name="Город", help_text="Введите город", **NULLABLE
    )
    first_name = models.CharField(
        max_length=40, verbose_name="Имя", help_text="Введите имя", **NULLABLE
    )
    last_name = models.CharField(
        max_length=40, verbose_name="Фамилия", help_text="Введите фамилию", **NULLABLE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-role",)

    def __str__(self):
        return f"{self.email} - {self.role} - {self.get_full_name() or ''}"
