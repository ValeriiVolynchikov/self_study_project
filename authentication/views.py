from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet

from authentication.models import User
from authentication.serializers import UserSerializer
from .permissions import IsOwner, IsAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated


class UserViewSet(ModelViewSet):
    """
    API endpoint для регистрации и управления пользователями.
    - Регистрация (create): доступна всем (AllowAny)
    - Просмотр списка (list): доступен всем (AllowAny)
    - Детализация/редактирование: только для админов или владельцев
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin() | IsOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        if user.role == User.Role.ADMIN:
            return super().get_queryset()
        return User.objects.filter(id=user.id)

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        responses={201: UserSerializer, 400: "Неверные входные данные"},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение профиля пользователя",
        responses={200: UserSerializer, 404: "Пользователь не найден"},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
