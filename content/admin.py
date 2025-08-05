from django.contrib import admin

from .models import Course, Material, Section


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner")
    search_fields = ("title", "owner__email")
    list_filter = ("owner",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    list_filter = ("course",)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "section")
    list_filter = ("section",)
