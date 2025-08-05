from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import User
from content.models import Course, Material, Section
from testing.models import Answer as AnswerModel
from testing.models import Question as QuestionModel
from testing.models import Test as TestModel
from testing.models import TestAttempt as TestAttemptModel


class TestingViewsTestCase(APITestCase):
    """
    Тесты для модуля тестирования.
    Проверяют работу API для получения тестов и отправки результатов.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com", password="testpass", role="student"
        )
        self.client.force_authenticate(user=self.user)

        course = Course.objects.create(title="Course", owner=self.user)
        section = Section.objects.create(title="Section", course=course)
        material = Material.objects.create(
            title="Material", content="Content", section=section
        )

        self.test = TestModel.objects.create(title="Sample Test", material=material)
        self.question = QuestionModel.objects.create(
            test=self.test, text="What is 2+2?"
        )
        self.correct_answer = AnswerModel.objects.create(
            question=self.question, text="4", is_correct=True
        )
        self.wrong_answer = AnswerModel.objects.create(
            question=self.question, text="3", is_correct=False
        )

    def test_get_tests(self):
        """
        Тест получения списка тестов.
        Проверяет, что API возвращает корректный список тестов.
        """
        url = reverse("testing:test-list")  # URL от ViewSet
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], self.test.title)
        self.assertEqual(str(self.test), "Тест: Sample Test")
        self.assertEqual(str(self.question), "What is 2+2?")
        self.assertEqual(str(self.correct_answer), "4 (верный)")
        self.assertEqual(str(self.wrong_answer), "3 (неверный)")

    def test_submit_test_with_correct_answer(self):
        """
        Тест отправки теста с правильным ответом.
        Проверяет, что система корректно обрабатывает правильный ответ
        и возвращает 100% результат.
        """
        url = reverse("testing:submit-test", args=[self.test.id])
        data = {
            "answers": [
                {
                    "question_id": self.question.id,
                    "selected_answer_id": self.correct_answer.id,
                }
            ]
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], 100)
        self.assertTrue(response.data["passed"])

        attempt = TestAttemptModel.objects.get(user=self.user, test=self.test)
        self.assertEqual(attempt.score, 100)
        self.assertTrue(attempt.passed)
        self.assertEqual(len(response.data["details"]), 1)
        self.assertTrue(response.data["details"][0]["is_correct"])

    def test_submit_test_with_wrong_answer(self):
        """
        Тест отправки теста с неправильным ответом.
        Проверяет, что система корректно обрабатывает неправильный ответ
        и возвращает 0% результат.
        """
        url = reverse("testing:submit-test", args=[self.test.id])
        data = {
            "answers": [
                {
                    "question_id": self.question.id,
                    "selected_answer_id": self.wrong_answer.id,
                }
            ]
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], 0)
        self.assertFalse(response.data["passed"])

        attempt = TestAttemptModel.objects.get(user=self.user, test=self.test)
        self.assertEqual(attempt.score, 0)
        self.assertFalse(attempt.passed)
        self.assertEqual(len(response.data["details"]), 1)
        self.assertFalse(response.data["details"][0]["is_correct"])

    def test_submit_test_with_invalid_question_id(self):
        """
        Тест: один из question_id не существует.
        Ожидаем 400 Bad Request.
        """
        url = reverse("testing:submit-test", args=[self.test.id])
        data = {
            "answers": [
                {
                    "question_id": 9999,
                    "selected_answer_id": self.correct_answer.id,
                }
            ]
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
