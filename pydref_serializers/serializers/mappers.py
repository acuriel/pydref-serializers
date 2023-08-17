import logging
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, Callable
from uuid import UUID

from django.db.models import Field as DjangoField
from pydantic import IPvAnyAddress, Json

logger = logging.getLogger(__name__)


DJANGO_FIELD_MAP = {
    # Numerical related fields
    "AutoField": int,
    "BigAutoField": int,
    "IntegerField": int,
    "SmallIntegerField": int,
    "BigIntegerField": int,
    "PositiveIntegerField": int,
    "PositiveSmallIntegerField": int,
    "FloatField": float,
    "DecimalField": Decimal,
    # String related fields
    "CharField": str,
    "EmailField": str,
    "URLField": str,
    "SlugField": str,
    "TextField": str,
    "FilePathField": str,
    "FileField": str,
    "ImageField": str,
    # Other built-in fields
    "BooleanField": bool,
    "BinaryField": bytes,
    "DateField": date,
    "DateTimeField": datetime,
    "DurationField": timedelta,
    "TimeField": time,
    "UUIDField": UUID,
    "GenericIPAddressField": IPvAnyAddress,
    "JSONField": Json | dict | list,  # TODO: Configure this using default
}


_FieldMapper = Callable[[DjangoField], tuple[type, Any]]


def default_field_mapper(field: DjangoField) -> tuple[type, Any]:
    field_type = DJANGO_FIELD_MAP.get(field.__class__.__name__)
    if not field_type:
        logger.warning(f"Field {field} is not supported")
        field_type = Any
    field_config = {}
    return field_type, field_config
