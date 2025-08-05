from django.urls import include, path
from rest_framework.routers import SimpleRouter

from content.apps import ContentConfig
from content.views import CourseViewSet, MaterialViewSet, SectionViewSet

app_name = ContentConfig.name


router = SimpleRouter()
router.register(
    "courses", CourseViewSet, basename="courses"
)  # Эндпоинты для работы с курсами
router.register(
    "sections", SectionViewSet, basename="sections"
)  # Эндпоинты для работы с разделами
router.register(
    "materials", MaterialViewSet, basename="materials"
)  # Эндпоинты для работы с материалами

urlpatterns = [
    path("", include(router.urls)),
]
