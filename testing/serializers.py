from rest_framework import serializers

from .models import Answer, Question, Test


class AnswerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ответов на вопросы теста.
    Используется для отображения вариантов ответов без информации о правильности.
    """

    class Meta:
        model = Answer
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вопросов теста.
    Включает вложенные варианты ответов (без информации о правильности).
    """

    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "answers"]


class TestSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тестов.
    Включает вложенные вопросы с вариантами ответов.
    """

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ["id", "title", "material", "questions"]


class UserAnswerSerializer(serializers.Serializer):
    """
    Сериализатор для ответа пользователя на один вопрос теста.
    Используется при отправке результатов теста.
    """

    question_id = serializers.IntegerField(
        help_text="ID вопроса, на который отвечает пользователь"
    )
    selected_answer_id = serializers.IntegerField(
        help_text="ID выбранного варианта ответа"
    )


class SubmitTestSerializer(serializers.Serializer):
    """
    Сериализатор для отправки результатов теста.
    Содержит список ответов пользователя на вопросы теста.
    """

    answers = UserAnswerSerializer(
        many=True, help_text="Список ответов пользователя на вопросы теста"
    )
