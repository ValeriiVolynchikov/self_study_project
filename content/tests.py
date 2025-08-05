from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import User
from content.models import Course, Material, Section

from .serializers import (CourseSerializer, MaterialSerializer,
                          SectionSerializer)


class ModelTests(APITestCase):
    """
    Тесты для моделей и сериализаторов контента.
    Проверяет корректность создания моделей и работу сериализаторов.
    """

    def setUp(self):
        """
        Настройка тестовых данных:
        - Создаем пользователей (учителя, студента, администратора)
        - Создаем тестовый курс, раздел и материал
        - Создаем "чужой" курс и раздел для проверки прав доступа
        """
        self.teacher = User.objects.create_user(
            email="teacher@example.com", password="testpass", role="teacher"
        )

        self.student = User.objects.create_user(
            email="student@example.com", password="studentpass", role="student"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )

        self.course = Course.objects.create(title="Test Course", owner=self.teacher)
        self.section = Section.objects.create(title="Test Section", course=self.course)
        self.material = Material.objects.create(
            title="Test Material", content="Test Content", section=self.section
        )

        # Создаем чужой курс, секцию и материал
        self.other_teacher = User.objects.create_user(
            email="other_teacher@example.com", password="testpass", role="teacher"
        )
        self.other_course = Course.objects.create(
            title="Other Course", owner=self.other_teacher
        )
        self.other_section = Section.objects.create(
            title="Other Section", course=self.other_course
        )

    def test_course_creation(self):
        """Проверяет корректность создания и строкового представления курса."""
        self.assertEqual(str(self.course), "Test Course")
        self.assertEqual(self.course.owner, self.teacher)

    def test_section_creation(self):
        """Проверяет корректность создания и строкового представления раздела."""
        self.assertEqual(str(self.section), "Test Course — Test Section")

    def test_material_creation(self):
        """Проверяет корректность создания и строкового представления материала."""
        self.assertEqual(str(self.material), "Test Section — Test Material")

    def test_course_serializer(self):
        """Проверяет корректность сериализации данных курса."""
        serializer = CourseSerializer(self.course)
        self.assertEqual(serializer.data["title"], "Test Course")
        self.assertEqual(serializer.data["owner"], self.teacher.id)

    def test_section_serializer(self):
        """Проверяет корректность сериализации данных раздела."""
        serializer = SectionSerializer(self.section)
        self.assertEqual(serializer.data["title"], "Test Section")
        self.assertEqual(serializer.data["course"], self.course.id)

    def test_material_serializer(self):
        """Проверяет корректность сериализации данных материала."""
        serializer = MaterialSerializer(self.material)
        self.assertEqual(serializer.data["title"], "Test Material")
        self.assertEqual(serializer.data["section"], self.section.id)


class CourseViewSetTests(APITestCase):
    """
    Тесты для CourseViewSet.
    Проверяет работу API для управления курсами.
    """

    def setUp(self):
        """Настройка тестовых данных для тестов CourseViewSet."""
        self.teacher = User.objects.create_user(
            email="teacher@example.com", password="testpass", role="teacher"
        )
        self.student = User.objects.create_user(
            email="student@example.com", password="studentpass", role="student"
        )
        self.course = Course.objects.create(title="Test Course", owner=self.teacher)

    def test_list_courses(self):
        """
        Проверяет получение списка курсов.
        Должен возвращать статус 200 OK для аутентифицированного пользователя.
        """
        url = reverse("content:courses-list")
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_course_as_teacher(self):
        """
        Проверяет создание курса преподавателем.
        Должен возвращать статус 201 Created и увеличивать количество курсов.
        """
        url = reverse("content:courses-list")
        data = {"title": "New Course", "description": "New Desc"}
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_update_course_as_owner(self):
        """
        Проверяет обновление курса владельцем.
        Должен возвращать статус 200 OK и обновлять данные курса.
        """
        url = reverse("content:courses-detail", args=[self.course.id])
        data = {"title": "Updated Title"}
        self.client.force_authenticate(user=self.teacher)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Updated Title")


class SectionViewSetTests(APITestCase):
    """
    Тесты для SectionViewSet.
    Проверяет работу API для управления разделами курсов.
    """

    def setUp(self):
        """Настройка тестовых данных для тестов SectionViewSet."""
        self.teacher = User.objects.create_user(
            email="teacher@example.com", password="testpass", role="teacher"
        )
        self.other_teacher = User.objects.create_user(
            email="other_teacher@example.com", password="testpass", role="teacher"
        )
        self.course = Course.objects.create(title="Test Course", owner=self.teacher)
        self.other_course = Course.objects.create(
            title="Other Course", owner=self.other_teacher
        )
        self.section = Section.objects.create(title="Test Section", course=self.course)

    def test_create_section_as_teacher(self):
        """
        Проверяет создание раздела преподавателем.
        Должен возвращать статус 201 Created.
        """
        url = reverse("content:sections-list")
        data = {"title": "New Section", "course": self.course.id}
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_sees_only_own_section(self):
        """
        Проверяет, что преподаватель видит только свои разделы.
        Должен возвращать только разделы, принадлежащие курсам преподавателя.
        """
        Section.objects.create(title="Other Section", course=self.other_course)
        self.client.force_authenticate(user=self.teacher)
        url = reverse("content:sections-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in response.data]
        self.assertIn("Test Section", titles)
        self.assertNotIn("Other Section", titles)


class MaterialViewSetTests(APITestCase):
    """
    Тесты для MaterialViewSet.
    Проверяет работу API для управления учебными материалами.
    """

    def setUp(self):
        """Настройка тестовых данных для тестов MaterialViewSet."""
        self.teacher = User.objects.create_user(
            email="teacher@example.com", password="testpass", role="teacher"
        )
        self.other_teacher = User.objects.create_user(
            email="other_teacher@example.com", password="testpass", role="teacher"
        )
        self.course = Course.objects.create(title="Test Course", owner=self.teacher)
        self.other_course = Course.objects.create(
            title="Other Course", owner=self.other_teacher
        )
        self.section = Section.objects.create(title="Test Section", course=self.course)
        self.other_section = Section.objects.create(
            title="Other Section", course=self.other_course
        )
        self.material = Material.objects.create(
            title="Test Material", content="Test Content", section=self.section
        )

    def test_create_material_as_teacher(self):
        """
        Проверяет создание материала преподавателем.
        Должен возвращать статус 201 Created.
        """
        url = reverse("content:materials-list")
        data = {
            "title": "New Material",
            "content": "New Content",
            "section": self.section.id,
        }
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_sees_only_own_materials(self):
        """
        Проверяет, что преподаватель видит только свои материалы.
        Должен возвращать только материалы, принадлежащие разделам преподавателя.
        """
        Material.objects.create(
            title="Other Material", content="Other Content", section=self.other_section
        )
        self.client.force_authenticate(user=self.teacher)
        url = reverse("content:materials-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in response.data]
        self.assertIn("Test Material", titles)
        self.assertNotIn("Other Material", titles)
