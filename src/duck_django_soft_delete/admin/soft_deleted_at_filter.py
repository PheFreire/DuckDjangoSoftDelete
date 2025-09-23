from django.contrib.admin import SimpleListFilter


class SoftDeletedAtFilter(SimpleListFilter):
    title = "Soft Delete"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return [
            ("no", "Not Deleted"),
            ("yes", "Deleted"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset.filter(deleted_at__isnull=True)

        elif self.value() == "yes":
            return queryset.filter(deleted_at__isnull=False)

        return queryset
