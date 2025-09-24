<p align="center">
  <img src="https://github.com/PheFreire/DuckDjangoSoftDelete/blob/main/assets/logo.png" alt="DuckDI Logo" width="150" />
</p>

# duck-django-soft-delete

Pragmatic **soft delete framework for Django**.  
It provides a safe and transparent way to "delete" records by marking them with a timestamp instead of permanently removing them from the database.

This approach is useful when you need:
- Data recovery after accidental deletions;
- Historical/audit tracking;
- To keep database integrity while still hiding records from normal queries;
- To allow reusing unique keys (with conditional uniqueness).

---

## Features

- `deleted_at` field automatically added to your models;
- Ready-to-use managers:
  - `objects` → filters out deleted records;
  - `everything` → returns all records (including deleted);
- `soft_delete()` and `restore()` methods;
- **Admin** integration: filter by deletion status + actions for *Soft Delete* and *Restore*;
- Helper `build_prefetches()` to automatically prefetch only alive related records;
- Supports **partial unique constraints** in Postgres (unique only among alive records).

---

## Installation

```bash
pip install duck-django-soft-delete
```

Add to your project and import:

```python
# settings.py
INSTALLED_APPS = [
  # ...
  "duck_django_soft_delete",
]
```

---

## Concept

### Abstract base

```python
from duck_django_soft_delete.table.soft_delete_table import SoftDeleteTable

class MyModel(SoftDeleteTable):
    # your fields...
```

`SoftDeleteTable` defines:
- Model time stamp fields: `created_at`, `updated_at`
- Soft delete model field: `deleted_at`
- Django, soft delete and restore model methods: `soft_delete()` / `restore()`
- Django prefetch_related method for soft delete `build_prefetches(relations: list[str]) -> list[Prefetch|str]`
- Load django model as BaseModel Dto: `as_dto(include_fks: bool = False, show_deleted: bool = False) -> BaseModel` (abstract method — implement in your model)

### Managers

- `objects` → **alive only** (`deleted_at IS NULL`)  
- `everything` → **all** (alive and deleted)

---

## Real example

### Model with conditional uniqueness (Postgres)

```python
from duck_django_soft_delete.table.soft_delete_table import SoftDeleteTable
from django.db import models
from uuid import uuid4

class Item(SoftDeleteTable):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, default="")
    is_public = models.BooleanField(default=True)
    
    foreign_key_exemple = models.ForeignKey(
		"foreign_key_exemple.ForeignKeyExemple",
		on_delete=models.CASCADE,
		db_column="foreign_key_exemple_id",
		related_name="foreign_key_exemples",
	)
	
	class Meta(SoftDeleteTable.Meta):
		db_table = "items"
```

### Admin

```python
from duck_django_soft_delete.admin.soft_delete_admin import SoftDeleteAdmin
from django.contrib import admin
from item import Item

@admin.register(Item)
class ItemAdmin(SoftDeleteAdmin):
    list_display = (
        "uuid", 
        "name",
        "is_public",
        "created_at", 
        "updated_at", 
        "deleted_at",
    )
    list_filter = [
	    *SoftDeleteAdmin.list_filter, 
	    "is_public", 
	    "foreign_key_exemple",
	    "updated_at",
	]
    search_fields = ("name", "is_public", "foreign_key_exemple__id", )

    # ... your @admin.display helpers
```

> `SoftDeleteAdmin` provides:
> - filter `SoftDeletedAtFilter` (Not Deleted / Deleted);
> - actions “Soft delete selected” and “Restore selected”;
> - `get_queryset` using `everything` so admin sees all records.

---

## Usage

```python
obj = Item.objects.create(name="X")
obj.soft_delete()           # sets deleted_at = now()
obj.restore()               # clears deleted_at
Item.objects.all()      # only alive
Item.everything.all()   # all
```

### Prefetch alive-only relations
If you want to prefetch only alive children **when** the related model also inherits `SoftDeleteTable`:

```python
qs = Item.objects.all().prefetch_related(
    *Item.build_prefetches(["foreign_key_exemples", ])
)
```

- If the relation **inherits** `SoftDeleteTable`, prefetch uses its alive manager.
- If it does **not**, falls back to standard Django prefetch.

---

## Best practices

- **Postgres**: use `UniqueConstraint(..., condition=Q(deleted_at__isnull=True))` for uniqueness only on alive records. 
```python
	class Meta(SoftDeleteTable.Meta):
		db_table = "items"
		constraints = [
			models.UniqueConstraint(
				fields=["foreign_key_exemple", "name"],
				condition=Q(deleted_at__isnull=True),
				name="unique_item_name_per_foreign_key_exemple_not_deleted",
			)
		]
```

- Document whether you override `Model.delete()` to do soft delete by default (this lib does not enforce — you can choose to keep `delete()` as hard delete).

---

## Compatibility

- **Django**: 4.2+
- **Python**: 3.10+

---

## Admin — details

- Filter: “Soft Delete” → Not Deleted / Deleted  
- Actions:
  - **Soft delete selected**: calls `soft_delete()` on alive items;
  - **Restore selected**: calls `restore()` on deleted items;
- `get_queryset` uses `model.everything.all()` so admin shows all records.

> Tip: you can remove Django’s default `delete_selected` action to avoid accidental hard deletes.

---

## Tests

See the `tests/` folder in this repo (pytest + pytest-django), covering:
- Managers (`objects` vs `everything`);
- `soft_delete()` and `restore()`;
- Partial unique (Postgres);
- Admin actions;
- `build_prefetches()`.

---

## License
MIT

