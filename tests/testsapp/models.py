from uuid import uuid4
from django.db import models
from django.db.models import Q

from duck_django_soft_delete.table.soft_delete_table import SoftDeleteTable

class NonSoftChild(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=64, default="child")

    class Meta:
        app_label = "testsapp"


class Author(SoftDeleteTable):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False) 
    name = models.CharField(max_length=128)

    class Meta(SoftDeleteTable.Meta):
        app_label = "testsapp"


class Setting(SoftDeleteTable):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=128)

    class Meta(SoftDeleteTable.Meta):
        app_label = "testsapp"


class MasterKey(SoftDeleteTable):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=128)

    class Meta(SoftDeleteTable.Meta):
        app_label = "testsapp"


class Research(SoftDeleteTable):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, default="") 
    is_public = models.BooleanField(default=bool)

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="researches")
    setting = models.ForeignKey(Setting, on_delete=models.CASCADE, related_name="researches")
    master_key = models.ForeignKey(MasterKey, on_delete=models.CASCADE, related_name="researches")
 
    non_soft_children = models.ManyToManyField(NonSoftChild, related_name="researches", blank=True)

    class Meta(SoftDeleteTable.Meta):
        app_label = "testsapp"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "name", "master_key"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_research_name_per_author_alive",
            )
        ]

