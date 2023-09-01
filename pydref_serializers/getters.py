from typing import Any, Callable, Collection

from django.db.models import Field as DjangoField
from django.db.models import Model as DjangoModel

####################
#      TYPES       #
####################

_FieldGetter = Callable[[type[DjangoModel], Collection[str] | None], dict[type, Any]]


####################
#    FUNCTIONS     #
####################


def default_get_fields(
    model: type[DjangoModel],
    fields: Collection[str] = None,
) -> Collection[DjangoField]:
    """
    Returns a collection of Django model fields for the given model.

    Args:
        model: The Django model to retrieve fields from.
        fields: Optional collection of field names to retrieve. If not provided, all fields will be returned.

    Returns:
        A collection of Django model fields.
    """
    all_fields = model._meta.fields

    if fields is not None:
        return [field for field in all_fields if field.name in fields]
    return all_fields
