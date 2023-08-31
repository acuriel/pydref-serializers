from typing import Any, Callable, Collection

from django.db.models import Field as DjangoField
from django.db.models import Model as DjangoModel

_FieldGetter = Callable[[type[DjangoModel], Collection[str] | None], dict[type, Any]]


def default_get_fields(
    model: type[DjangoModel],
    fields: Collection[str] = None,
) -> Collection[DjangoField]:
    all_fields = model._meta.fields

    if fields is not None:
        return [field for field in all_fields if field.name in fields]
    return all_fields
