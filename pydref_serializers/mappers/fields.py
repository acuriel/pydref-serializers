import logging
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, IntEnum, StrEnum
from typing import Annotated, Any, Callable, get_args, get_origin
from uuid import UUID

from django.db.models import Field as DjangoField
from pydantic import AnyUrl, EmailStr, Field, FilePath, IPvAnyAddress, Json, PositiveInt

logger = logging.getLogger(__name__)


DJANGO_FIELD_MAP = {
    # Numerical related fields
    "AutoField": int,
    "BigAutoField": int,
    "IntegerField": int,
    "SmallIntegerField": int,
    "BigIntegerField": int,
    "PositiveIntegerField": PositiveInt,
    "PositiveSmallIntegerField": PositiveInt,
    "FloatField": float,
    "DecimalField": Decimal,
    # String related fields
    "CharField": str,
    "TextField": str,
    "SlugField": str,
    "EmailField": EmailStr,
    "URLField": AnyUrl,
    "FilePathField": FilePath,
    "FileField": FilePath,
    "ImageField": FilePath,
    # Other built-in fields
    "BooleanField": bool,
    "BinaryField": bytes,
    "DateField": date,
    "DateTimeField": datetime,
    "DurationField": timedelta,
    "TimeField": time,
    "UUIDField": UUID,
    "GenericIPAddressField": IPvAnyAddress,
    "JSONField": Json,
}


_FieldMapper = Callable[[DjangoField, bool], tuple[type, Any]]


def _get_base_type(_type: type) -> type:
    origin = get_origin(_type)
    if origin is Annotated:
        return get_args(_type)[0]
    return _type


def _get_field_default_config(field) -> dict:
    default_config = {}
    if field.has_default():
        if callable(field.default):
            default_config["default_factory"] = field.get_default
        else:
            default_config["default"] = field.default
    return default_config


def _get_enum_class(base_type: type) -> type[Enum]:
    if issubclass(base_type, int):
        return IntEnum
    elif issubclass(base_type, str):
        return StrEnum
    else:
        return Enum


def _get_pydantic_field_type(field: DjangoField, *, partial=False) -> tuple[type, type]:
    basic_type = DJANGO_FIELD_MAP.get(field.__class__.__name__)
    if not basic_type:
        logger.warning(f"Field {field} is not supported")
        basic_type = Any

    pydantic_field_type = basic_type
    base_type = _get_base_type(basic_type)
    if field.choices:
        enum_class = _get_enum_class(base_type)
        enum_name = f"{field.name.title()}Enum"
        enum_obj = enum_class(
            enum_name, [(choice[1], choice[0]) for choice in field.choices]
        )
        pydantic_field_type = enum_obj

    if field.null or partial:
        pydantic_field_type = pydantic_field_type | None
    return pydantic_field_type, base_type


def _get_mapped_validators(field: DjangoField) -> list[Callable]:
    # TODO: Implement this
    pass


def default_field_mapper(field: DjangoField, *, partial=False) -> tuple[type, Field]:
    pydantic_field_type, basic_type = _get_pydantic_field_type(field, partial=partial)
    field_config = {}
    if issubclass(basic_type, str):
        field_config["min_length"] = 0 if field.blank else 1
        if field.max_length:
            field_config["max_length"] = field.max_length
    field_config |= _get_field_default_config(field)
    _get_mapped_validators(field)

    return pydantic_field_type, Field(**field_config)
