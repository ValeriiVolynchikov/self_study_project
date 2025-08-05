from rest_framework import serializers

from .models import Course, Material, Section


class MaterialSerializer(serializers.ModelSerializer):
    """
    Сериализатор для учебных материалов.
    Позволяет создавать, просматривать и редактировать материалы.
    """

    class Meta:
        model = Material
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для разделов курса.
    Включает вложенные материалы этого раздела (только для чтения).
    """

    materials = MaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для курсов.
    Включает вложенные разделы этого курса (только для чтения).
    Поле owner доступно только для чтения - устанавливается автоматически как текущий пользователь.
    """

    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["owner"]
