from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Course(models.Model):
    """
    Модель курса, представляющая учебный курс в системе.
    Каждый курс принадлежит преподавателю (owner) и может содержать несколько разделов.
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Название курса",
        help_text="Введите название курса (максимум 255 символов)",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание курса",
        help_text="Введите описание курса (необязательно)",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец курса",
        help_text="Преподаватель, создавший курс",
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Section(models.Model):
    """
    Модель раздела курса. Каждый раздел принадлежит определенному курсу
    и может содержать несколько учебных материалов.
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Название раздела",
        help_text="Введите название раздела (максимум 255 символов)",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="Курс",
        help_text="Курс, к которому относится этот раздел",
    )

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    class Meta:
        verbose_name = "Раздел курса"
        verbose_name_plural = "Разделы курса"


# https://www.youtube.com/@sobolevn/videos
class Material(models.Model):
    """
    Модель учебного материала. Каждый материал принадлежит определенному разделу
    и содержит контент для изучения.
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Название материала",
        help_text="Введите название учебного материала (максимум 255 символов)",
    )
    content = models.TextField(
        verbose_name="Содержание материала",
        help_text="Введите содержание учебного материала",
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="Раздел",
        help_text="Раздел, к которому относится этот материал",
    )

    def __str__(self):
        return f"{self.section.title} — {self.title}"

    class Meta:
        verbose_name = "Учебный материал"
        verbose_name_plural = "Учебные материалы"
