from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .apps import TestingConfig
from .views import SubmitTestView, TestViewSet

app_name = TestingConfig.name

router = DefaultRouter()
router.register("tests", TestViewSet)  # Эндпоинты для работы с тестами (чтение)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "tests/<int:test_id>/submit/", SubmitTestView.as_view(), name="submit-test"
    ),  # Эндпоинт для отправки результатов теста
]
