from typing import Any, Callable, Collection

from django.db.models import Field as DjangoField
from django.db.models import Model as DjangoModel

_FieldGetter = Callable[[type[DjangoModel]], dict[type, Any]]


def default_get_fields(
    model: type[DjangoModel],
    *,
    include: Collection[str] = None,
    exclude: Collection[str] = None
) -> Collection[DjangoField]:
    all_fields = model._meta.fields

    if include and exclude:
        raise ValueError("Cannot include and exclude fields at the same time")
    if include:
        return [field for field in all_fields if field.name in include]
    if exclude:
        return [field for field in all_fields if field.name not in exclude]
    return all_fields
