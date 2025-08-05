from django.conf import settings
from django.db import models

from content.models import Material

User = settings.AUTH_USER_MODEL


class Test(models.Model):
    """
    Модель теста, связанного с учебным материалом.
    Каждый тест содержит набор вопросов и привязан к одному материалу.
    """

    material = models.OneToOneField(
        Material,
        on_delete=models.CASCADE,
        related_name="test",
        verbose_name="Учебный материал",
        help_text="Материал, к которому привязан этот тест",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название теста",
        help_text="Введите название теста (максимум 255 символов)",
    )

    def __str__(self):
        return f"Тест: {self.title}"

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"


class Question(models.Model):
    """
    Модель вопроса в тесте. Каждый вопрос принадлежит определенному тесту
    и содержит несколько вариантов ответа.
    """

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Тест",
        help_text="Тест, к которому относится этот вопрос",
    )
    text = models.TextField(
        verbose_name="Текст вопроса", help_text="Введите текст вопроса"
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Answer(models.Model):
    """
    Модель ответа на вопрос. Каждый ответ принадлежит определенному вопросу
    и может быть помечен как правильный.
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
        help_text="Вопрос, к которому относится этот ответ",
    )
    text = models.CharField(
        max_length=255,
        verbose_name="Текст ответа",
        help_text="Введите текст ответа (максимум 255 символов)",
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="Правильный ответ",
        help_text="Отметьте, если это правильный вариант ответа",
    )

    def __str__(self):
        return f"{self.text} ({'верный' if self.is_correct else 'неверный'})"

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"


class TestAttempt(models.Model):
    """
    Модель попытки прохождения теста пользователем.
    Хранит результаты прохождения теста конкретным пользователем.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, проходивший тест",
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        verbose_name="Тест",
        help_text="Тест, который проходил пользователь",
    )
    score = models.IntegerField(
        verbose_name="Результат", help_text="Процент правильных ответов"
    )
    passed = models.BooleanField(
        verbose_name="Пройден", help_text="Успешно ли пройден тест"
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время прохождения",
        help_text="Время завершения теста",
    )

    class Meta:
        verbose_name = "Попытка прохождения теста"
        verbose_name_plural = "Попытки прохождения тестов"
        ordering = ["-submitted_at"]
