import pytest
from pydantic import BaseModel
from tests.testsapp.models import Author, Setting, MasterKey, Research

@pytest.mark.django_db
def test_as_dto_returns_pydantic_models():
    a = Author.objects.create(name="A")
    s = Setting.objects.create(name="S")
    m = MasterKey.objects.create(name="M")
    r = Research.objects.create(name="R", author=a, setting=s, master_key=m)

    for dto in (a.as_dto(), s.as_dto(), m.as_dto(), r.as_dto()):
        assert isinstance(dto, BaseModel)
        assert hasattr(dto, "dict")
