from rest_framework.test import APITestCase

from authentication.models import User
from authentication.serializers import UserSerializer


class UserSerializerTests(APITestCase):
    """Тесты для проверки валидации и создания пользователей через UserSerializer"""

    def test_create_user_success(self):
        """Тест успешного создания пользователя с валидными данными"""
        data = {
            "email": "user@example.com",
            "role": User.Role.STUDENT,
            "first_name": "John",
            "last_name": "Doe",
            "city": "Moscow",
            "password": "strongpassword123",
            "password_confirm": "strongpassword123",
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.role, data["role"])
        self.assertTrue(user.check_password(data["password"]))
        self.assertTrue(user.is_active)

    def test_password_mismatch(self):
        """Тест ошибки валидации при несовпадении паролей"""
        data = {
            "email": "user@example.com",
            "role": User.Role.STUDENT,
            "first_name": "John",
            "last_name": "Doe",
            "city": "Moscow",
            "password": "password1",
            "password_confirm": "password2",
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            serializer.errors["non_field_errors"][0], "Пароли не совпадают"
        )

    def test_cannot_choose_admin_role(self):
        """Тест запрета самостоятельного назначения роли администратора"""
        data = {
            "email": "adminlike@example.com",
            "role": User.Role.ADMIN,
            "first_name": "Admin",
            "last_name": "User",
            "city": "Moscow",
            "password": "adminpass123",
            "password_confirm": "adminpass123",
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "Нельзя выбрать роль администратора",
        )
