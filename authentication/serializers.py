from rest_framework import serializers

from authentication.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации и управления пользователями.

    Обеспечивает:
    - Регистрацию пользователей с подтверждением пароля
    - Проверку ролей (запрещает самостоятельное назначение роли администратора)
    - Хеширование паролей
    """

    password = serializers.CharField(
        write_only=True, help_text="Пароль пользователя (будет захеширован)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Подтверждение пароля (должно совпадать с полем password)",
    )

    class Meta:
        model = User
        fields = (
            "email",
            "role",
            "first_name",
            "last_name",
            "city",
            "password",
            "password_confirm",
        )
        extra_kwargs = {
            "email": {"help_text": "Уникальный email пользователя"},
            "role": {"help_text": "Роль пользователя (student/teacher)"},
            "first_name": {"help_text": "Имя пользователя"},
            "last_name": {"help_text": "Фамилия пользователя"},
            "city": {"help_text": "Город проживания"},
        }

    def validate(self, data):
        """
        Проверка данных регистрации:
        - Совпадение паролей
        - Запрет назначения роли администратора
        """
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают")
        if data.get("role") == User.Role.ADMIN:
            raise serializers.ValidationError("Нельзя выбрать роль администратора")
        return data

    def create(self, validated_data):
        """
        Создание и возврат нового пользователя с хешированным паролем.
        По умолчанию устанавливает пользователя как активного.
        """
        validated_data.pop("password_confirm")  # Удаляем поле подтверждения
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user
    