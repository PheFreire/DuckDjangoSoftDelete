import pytest
from django.db.models import Prefetch

from tests.testsapp.models import Research

@pytest.mark.django_db
def test_build_prefetches_returns_prefetch_for_softdelete_relations():
    prefetches = Research.build_prefetches(["author", "setting", "master_key"])
    assert all(isinstance(p, Prefetch) for p in prefetches)
    for p in prefetches:
        sql = str(p.queryset.query)
        assert "deleted_at" in sql and "is null" in sql.lower()

@pytest.mark.django_db
def test_build_prefetches_fallback_for_non_soft_model():
    prefetches = Research.build_prefetches(["non_soft_children"])
    assert prefetches == ["non_soft_children"]

@pytest.mark.django_db
def test_build_prefetches_invalid_relation_raises():
    with pytest.raises(Exception):
        Research.build_prefetches(["invalid"])

