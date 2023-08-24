from typing import Any, Callable, Collection

from django.db.models import Field as DjangoField
from django.db.models import Model as DjangoModel

_FieldGetter = Callable[
    [type[DjangoModel], Collection[str] | None, Collection[str] | None], dict[type, Any]
]


def default_get_fields(
    model: type[DjangoModel],
    *,
    include_fields: Collection[str] = None,
    exclude_fields: Collection[str] = None
) -> Collection[DjangoField]:
    all_fields = model._meta.fields

    if include_fields and exclude_fields:
        raise ValueError("Cannot include and exclude fields at the same time")
    if include_fields:
        return [field for field in all_fields if field.name in include_fields]
    if exclude_fields:
        return [field for field in all_fields if field.name not in exclude_fields]
    return all_fields
