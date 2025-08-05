from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings

from .models import Answer, Test, TestAttempt
from .serializers import SubmitTestSerializer, TestSerializer


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с тестами (только чтение).

    Доступные действия:
    - list: Получить список всех тестов
    - retrieve: Получить детальную информацию о тесте (с вопросами и ответами)

    Тесты доступны только для чтения всем аутентифицированным пользователям.
    """

    queryset = Test.objects.all()
    serializer_class = TestSerializer


class SubmitTestView(APIView):
    """
    API для отправки результатов теста.

    Принимает список ответов пользователя на вопросы теста,
    вычисляет результат (процент правильных ответов) и сохраняет попытку.

    Тест считается пройденным, если набрано 70% или более правильных ответов.
    """

    @swagger_auto_schema(
        request_body=SubmitTestSerializer,
        responses={
            200: "Результат тестирования (score: процент, passed: пройден ли тест)",
            404: "Тест не найден",
            400: "Неверный формат данных",
        },
        operation_description="Отправить результаты прохождения теста",
        operation_summary="Отправка результатов теста",
    )
    def post(self, request, test_id):
        """
        Обрабатывает отправку результатов теста.

        Параметры:
        - test_id: ID теста, который проходит пользователь
        - answers: список ответов пользователя в формате {question_id, selected_answer_id}

        Возвращает:
        - score: процент правильных ответов
        - passed: true/false — пройден ли тест (>=70%)
        - details: список вопросов с результатами пользователя
        """
        # Валидация входных данных
        serializer = SubmitTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем тест или 404
        test = get_object_or_404(Test, pk=test_id)

        # Формируем словарь: question_id -> selected_answer_id
        user_answers = {
            answer["question_id"]: answer["selected_answer_id"]
            for answer in serializer.validated_data["answers"]
        }

        question_ids = user_answers.keys()
        answer_ids = user_answers.values()

        # Загружаем все вопросы по ID, используем in_bulk для получения словаря {id: Question}
        questions_dict = test.questions.in_bulk(question_ids)

        # Проверяем, что ВСЕ question_id действительно существуют
        if len(questions_dict) < len(user_answers):
            return Response(
                {"detail": "Невалидные вопросы в ответах."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Загружаем ответы, выбранные пользователем, с привязкой к этому тесту
        answers = Answer.objects.filter(
            id__in=answer_ids,
            question_id__in=question_ids,
            question__test=test,
        ).select_related("question")

        # Подсчет правильных и формирование подробного отчета
        correct = 0
        details = []

        for answer in answers:
            is_correct = (
                answer.is_correct and user_answers.get(answer.question_id) == answer.id
            )

            if is_correct:
                correct += 1

            # Добавляем информацию в отчет
            details.append(
                {
                    "question_id": answer.question_id,
                    "question_text": answer.question.text,
                    "selected_answer_id": answer.id,
                    "selected_answer_text": answer.text,
                    "is_correct": is_correct,
                }
            )

        # Считаем общее количество вопросов в тесте
        total = test.questions.count()

        # Вычисляем процент правильных
        score = round((correct / total) * 100)
        passed = score >= settings.TEST_PASS_THRESHOLD

        # Сохраняем попытку пользователя
        TestAttempt.objects.create(
            user=request.user, test=test, score=score, passed=passed
        )

        # Возвращаем результат теста и подробный разбор
        return Response(
            {"score": score, "passed": passed, "details": details},
            status=status.HTTP_200_OK,
        )
