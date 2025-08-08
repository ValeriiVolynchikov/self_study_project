from django.contrib.auth.models import AnonymousUser
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsAdmin, IsOwner, IsTeacherOrAdmin as IsTeacher

from .models import Course, Material, Section
from .serializers import (CourseSerializer, MaterialSerializer,
                          SectionSerializer)


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с курсами.

    Доступные действия:
    - list: Получить список курсов (для всех аутентифицированных пользователей)
    - retrieve: Получить детали курса (для всех аутентифицированных пользователей)
    - create: Создать курс (только для администраторов и преподавателей)
    - update/partial_update: Обновить курс (только для администраторов или владельцев-преподавателей)
    - destroy: Удалить курс (только для администраторов или владельцев-преподавателей)

    Преподаватели видят только свои курсы. Администраторы видят все курсы.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            # Разрешаем: Админ ИЛИ (Преподаватель И владелец)
            self.permission_classes = [IsAdmin | (IsTeacher & IsOwner)]
        elif self.action == 'create':
            # Разрешаем: Админ ИЛИ Преподаватель
            self.permission_classes = [IsAdmin | IsTeacher]
        else:
            # Для list/retrieve - только аутентификация
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Автоматически назначаем текущего пользователя владельцем"""
        if self.request.user.role in ['teacher', 'admin']:
            serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Фильтрует курсы в зависимости от роли пользователя."""
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return Course.objects.none()
        if user.role == 'teacher':
            return Course.objects.filter(owner=user)
        return super().get_queryset()


class SectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с разделами курсов.

    Доступные действия:
    - list: Получить список разделов (для всех аутентифицированных пользователей)
    - retrieve: Получить детали раздела (для всех аутентифицированных пользователей)
    - create: Создать раздел (только для администраторов или владельцев-преподавателей)
    - update/partial_update: Обновить раздел (только для администраторов или владельцев-преподавателей)
    - destroy: Удалить раздел (только для администраторов или владельцев-преподавателей)

    Преподаватели видят только разделы своих курсов. Администраторы видят все разделы.
    """

    serializer_class = SectionSerializer

    def get_queryset(self):
        """Фильтрует разделы в зависимости от роли пользователя."""
        user = self.request.user
        if isinstance(user, AnonymousUser) or not hasattr(user, "role"):
            return Material.objects.none()
        if user.role == "teacher":
            return Section.objects.filter(course__owner=user)
        return Section.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdmin | (IsTeacher & IsOwner)]

        return super().get_permissions()


class MaterialViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с учебными материалами.

    Доступные действия:
    - list: Получить список материалов (для всех аутентифицированных пользователей)
    - retrieve: Получить детали материала (для всех аутентифицированных пользователей)
    - create: Создать материал (только для администраторов или владельцев-преподавателей)
    - update/partial_update: Обновить материал (только для администраторов или владельцев-преподавателей)
    - destroy: Удалить материал (только для администраторов или владельцев-преподавателей)

    Преподаватели видят только материалы своих курсов. Администраторы видят все материалы.
    """

    serializer_class = MaterialSerializer

    def get_queryset(self):
        """Фильтрует материалы в зависимости от роли пользователя."""
        user = self.request.user
        if isinstance(user, AnonymousUser) or not hasattr(user, "role"):
            return Material.objects.none()
        if user.role == "teacher":
            return Material.objects.filter(section__course__owner=user)

        return Material.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdmin | (IsTeacher & IsOwner)]

        return super().get_permissions()
