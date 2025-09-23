from django.db import models


class NonSoftDeletedQuerySet(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(deleted_at__isnull=True)
