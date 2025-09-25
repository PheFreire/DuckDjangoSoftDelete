from typing import Type

from django.db import models
from django.db.models.query import Prefetch
from django.utils import timezone

from duck_django_soft_delete.queryset.non_soft_deleted_query_set import (
    NonSoftDeletedQuerySet,
)

class SoftDeleteTable(models.Model):
    """
    Abstract base model that provides soft delete functionality via a 'deleted_at' field.

    Models inheriting from this class will gain:
    - A soft delete method that timestamps 'deleted_at'.
    - A restore method to nullify 'deleted_at'.
    - Two managers:
        - `objects`: filters out soft-deleted records by default.
        - `everything`: returns all records, including soft-deleted ones.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    everything = models.Manager()
    objects = NonSoftDeletedQuerySet()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marks the record as soft-deleted by setting the 'deleted_at' timestamp to now."""

        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        """Restores a soft-deleted record by clearing the 'deleted_at' field."""

        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @classmethod
    def build_prefetches(cls: Type["SoftDeleteTable"], relations: list[str]):
        prefetches = []

        for rel_name in relations:
            field = cls._meta.get_field(rel_name)
            related_model = getattr(field, "related_model", None)

            if (
                related_model
                and isinstance(related_model, type)
                and hasattr(related_model, "deleted_at")
                and issubclass(related_model, SoftDeleteTable)
            ):
                qs = related_model.objects.filter(deleted_at__isnull=True)
                prefetches.append(Prefetch(rel_name, queryset=qs))
            else:
                prefetches.append(rel_name)

        return prefetches
