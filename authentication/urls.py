from django.conf.urls.static import static
from django.urls import path
from drf_yasg.utils import swagger_auto_schema
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from authentication.apps import AuthenticationConfig
from authentication.views import UserViewSet
from config import settings

app_name = AuthenticationConfig.name

router = SimpleRouter()
router.register(
    "register",
    UserViewSet,
    basename="register",
)

urlpatterns = [
    path(
        "login/",
        swagger_auto_schema(
            method="post",
            operation_description="Получение пары JWT токенов (access + refresh)",
            responses={200: "Пара токенов", 400: "Неверные учетные данные"},
        )(TokenObtainPairView.as_view()),
        name="login",
    ),
    path(
        "token/refresh/",
        swagger_auto_schema(
            method="post",
            operation_description="Обновление access токена с помощью refresh токена",
            responses={200: "Новый access токен", 401: "Неверный refresh токен"},
        )(TokenRefreshView.as_view()),
        name="token_refresh",
    ),
] + router.urls
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
