import pytest
from tests.testsapp.models import Author, Setting, MasterKey, Research

@pytest.mark.django_db
def test_everything_includes_deleted():
    a = Author.objects.create(name="A")
    s = Setting.objects.create(name="S")
    m = MasterKey.objects.create(name="M")
    r = Research.objects.create(name="R", author=a, setting=s, master_key=m)
    r.soft_delete()

    assert Research.objects.count() == 0
    assert Research.everything.count() == 1
