from django.contrib import admin, messages

from duck_django_soft_delete.admin.soft_deleted_at_filter import (
    SoftDeletedAtFilter,
)


class SoftDeleteAdmin(admin.ModelAdmin):
    list_filter = [SoftDeletedAtFilter, "created_at", "updated_at"]
    readonly_fields = [
        "deleted_at",
    ]
    ordering = [
        "-created_at",
    ]

    @admin.action()
    def soft_delete_selected(self, request, queryset):
        updated = 0
        for obj in queryset:
            if obj.deleted_at is None:
                obj.soft_delete()
                updated += 1
        self.message_user(
            request, f"{updated} soft-deleted items.", messages.SUCCESS
        )

    @admin.action()
    def restore_selected(self, request, queryset):
        updated = 0
        for obj in queryset:
            if obj.deleted_at is not None:
                obj.restore()
                updated += 1
        self.message_user(
            request, f"{updated} restaured items.", messages.SUCCESS
        )

    actions = [
        "soft_delete_selected",
        "restore_selected",
    ]

    def get_queryset(self, request):
        return self.model.everything.all()
