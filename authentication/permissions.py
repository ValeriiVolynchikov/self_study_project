from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Проверяет, является ли пользователь администратором."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsTeacher(permissions.BasePermission):
    """Проверяет, является ли пользователь преподавателем."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"


class IsStudent(permissions.BasePermission):
    """Проверяет, является ли пользователь студентом."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем."""

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
