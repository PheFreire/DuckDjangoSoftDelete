import pytest
from django.db import connection
from tests.testsapp.models import Author, Setting, MasterKey, Research

postgres_required = pytest.mark.skipif(
    "postgresql" not in connection.settings_dict["ENGINE"],
    reason="Test requires PostgreSQL for partial unique constraint",
)

@pytest.mark.django_db
@postgres_required
def test_unique_partial_allows_reuse_when_soft_deleted():
    a = Author.objects.create(name="A")
    s = Setting.objects.create(name="S")
    m = MasterKey.objects.create(name="M")

    r1 = Research.objects.create(name="R", author=a, setting=s, master_key=m)
    r1.soft_delete()

    # Reuse combination because the original is soft-deleted
    r2 = Research.objects.create(name="R", author=a, setting=s, master_key=m)
    assert r2.pk != r1.pk
