import pytest
from tests.testsapp.models import Author, Setting, MasterKey, Research

@pytest.mark.django_db
def test_objects_excludes_soft_deleted(freeze_time):
    a = Author.objects.create(name="Alice")
    s = Setting.objects.create(name="Default")
    m = MasterKey.objects.create(name="MK")
    r1 = Research.objects.create(name="R1", author=a, setting=s, master_key=m)
    r2 = Research.objects.create(name="R2", author=a, setting=s, master_key=m)

    assert Research.objects.count() == 2
    r1.soft_delete()
    assert r1.deleted_at is not None
    assert Research.objects.count() == 1
    assert Research.everything.count() == 2

@pytest.mark.django_db
def test_restore_sets_deleted_at_none(freeze_time):
    a = Author.objects.create(name="A")
    s = Setting.objects.create(name="S")
    m = MasterKey.objects.create(name="M")
    r = Research.objects.create(name="R", author=a, setting=s, master_key=m)

    r.soft_delete()
    assert r.deleted_at is not None
    r.restore()
    r.refresh_from_db()
    assert r.deleted_at is None

@pytest.mark.django_db
def test_restore_is_idempotent(freeze_time):
    a = Author.objects.create(name="A")
    s = Setting.objects.create(name="S")
    m = MasterKey.objects.create(name="M")
    r = Research.objects.create(name="R", author=a, setting=s, master_key=m)
    r.restore(); r.restore()
    assert r.deleted_at is None
