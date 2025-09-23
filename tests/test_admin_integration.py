import pytest
from django.contrib import messages
from django.contrib.admin import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

from duck_django_soft_delete.admin.soft_deleted_at_filter import SoftDeletedAtFilter
from tests.testsapp.models import Research, Author, Setting, MasterKey

def make_request(method="get", path="/", data=None):
    rf = RequestFactory()
    req = getattr(rf, method.lower())(path, data=data or {})
     
    SessionMiddleware(lambda r: None).process_request(req)
    req.session.save()
     
    setattr(req, "_messages", FallbackStorage(req))
     
    req.user = AnonymousUser()
    return req


@pytest.mark.django_db
def test_admin_soft_delete_and_restore_actions():
    from duck_django_soft_delete.admin.soft_delete_admin import SoftDeleteAdmin

    site = AdminSite()
    admin_cls = SoftDeleteAdmin(Research, site)

    a = Author.objects.create(name="A")
    s = Setting.objects.create(name="S")
    m = MasterKey.objects.create(name="M")
    r = Research.objects.create(name="R", author=a, setting=s, master_key=m)

     
    req = make_request()
    qs = Research.everything.filter(pk=r.pk)
    admin_cls.soft_delete_selected(req, qs)
    r.refresh_from_db()
    assert r.deleted_at is not None

     
    msgs = list(messages.get_messages(req))
    assert any("soft-deleted items" in str(m) for m in msgs)

     
    req2 = make_request()
    qs2 = Research.everything.filter(pk=r.pk)
    admin_cls.restore_selected(req2, qs2)
    r.refresh_from_db()
    assert r.deleted_at is None

    msgs2 = list(messages.get_messages(req2))
    assert any("restaured items" in str(m) for m in msgs2)   


@pytest.mark.django_db
def test_admin_soft_deleted_filter():
     
    site = AdminSite()
    from duck_django_soft_delete.admin.soft_delete_admin import SoftDeleteAdmin

    admin_cls = SoftDeleteAdmin(Research, site)

    a = Author.objects.create(name="A")
    s = Setting.objects.create(name="S")
    m = MasterKey.objects.create(name="M")
    alive = Research.objects.create(name="Alive", author=a, setting=s, master_key=m)
    deleted = Research.objects.create(name="Deleted", author=a, setting=s, master_key=m)
    deleted.soft_delete()
 
    req = make_request(data={"deleted": "no"})
    f = SoftDeletedAtFilter(req, req.GET.copy(), Research, admin_cls)
    qs = f.queryset(req, Research.everything.all())
    assert qs.filter(pk=alive.pk).exists()
    assert not qs.filter(pk=deleted.pk).exists()
 
    req2 = make_request(data={"deleted": "yes"})
    f2 = SoftDeletedAtFilter(req2, req2.GET.copy(), Research, admin_cls)
    qs2 = f2.queryset(req2, Research.everything.all())
    assert not qs2.filter(pk=alive.pk).exists()
    assert qs2.filter(pk=deleted.pk).exists()

