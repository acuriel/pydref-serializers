from typing import Any, Callable

from django.db.models import Field as DjangoField
from django.db.models import Model as DjangoModel

_FieldGetter = Callable[[type[DjangoModel]], dict[type, Any]]


def default_get_fields(model: type[DjangoModel]) -> list[DjangoField]:
    return model._meta.fields
