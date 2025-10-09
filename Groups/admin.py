from django.contrib import admin
from .models import Group, Instructor
from django.utils.html import format_html


class InstructorAdmin(admin.ModelAdmin):
    list_display = ("name", "credentials")
    search_fields = ("name", "credentials")
    ordering = ("name",)


class GroupAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "instructor",
        "category",
        "image",
    ]
    list_filter = ("instructor",)
    search_fields = ("title", "instructor__name")
    ordering = ("title",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.image.url)
        return "No image uploaded"

    image_preview.short_description = "Image Preview"
    admin.site.register(Instructor, InstructorAdmin)


admin.site.register(Group, GroupAdmin)
