from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Только администраторы"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == "admin")


class IsTeacher(permissions.BasePermission):  # Добавляем класс IsTeacher
    """Только преподаватели"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == "teacher")


class IsOwner(permissions.BasePermission):
    """Владелец объекта или администратор"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsTeacherOrAdmin(permissions.BasePermission):
    """Преподаватели или администраторы"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role in ["admin", "teacher"])
