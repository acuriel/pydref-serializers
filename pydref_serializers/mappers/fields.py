import logging
from dataclasses import dataclass
from dataclasses import field as DataclassField
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, Tuple
from uuid import UUID

from django.db.models import Field as DjangoField
from pydantic import AnyUrl, EmailStr, Field, FilePath, IPvAnyAddress, Json, PositiveInt

logger = logging.getLogger(__name__)


####################
#      TYPES       #
####################

_FieldMapper = Callable[[DjangoField, bool], Tuple[type, Any]]


####################
#    CONSTANTS     #
####################

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


####################
#      CLASSES     #
####################


class NOT_PROVIDED:
    pass


@dataclass
class FieldDescriptor:
    """
    A descriptor for a Django model field.

    Attributes:
        name (str): The name of the field.
        django_field_type (type[DjangoField]): The type of the Django field.
        is_required (bool, optional): Whether the field is required. Defaults to True.
        default (Any | None, optional): The default value for the field. Defaults to None.
        allows_null (bool, optional): Whether the field allows null values. Defaults to False.
        choices (list[tuple[Any, str]] | None, optional): The choices for the field. Defaults to None.
        max_length (int | None, optional): The maximum length of the field. Defaults to None.
        min_length (int | None, optional): The minimum length of the field. Defaults to None.
    """

    name: str
    django_field_type: type[DjangoField]
    is_required: bool = True
    default: Any | None = NOT_PROVIDED
    allows_null: bool = False
    choices: list[tuple[Any, str]] | None = None
    max_length: int | None = None
    allows_blank: bool = False
    validators: list[Callable] | None = None


@dataclass
class FieldMapper:
    """
    A class that maps Django model fields to Pydantic fields.

    Attributes:
    -----------
    fields_map : Dict[str, Any]
        A dictionary that maps Django field types to Pydantic field types.
    """

    fields_map: Dict[str, Any] = DataclassField(
        default_factory=lambda: DJANGO_FIELD_MAP
    )

    def _get_field_descriptor(
        self, field: DjangoField, *, partial=False
    ) -> FieldDescriptor:
        """
        Returns a FieldDescriptor object for the given Django field.

        Parameters:
        -----------
        field : DjangoField
            The Django field to get the descriptor for.
        partial : bool, optional
            Whether the field is partial or not. Default is False.

        Returns:
        --------
        FieldDescriptor
            A FieldDescriptor object for the given Django field.
        """
        return FieldDescriptor(
            name=field.name,
            django_field_type=field.__class__,
            is_required=not (field.null or partial or field.has_default()),
            default=field.get_default if callable(field.default) else field.default,
            allows_null=field.null,
            allows_blank=field.blank,
            choices=field.choices,
            max_length=field.max_length,
        )

    def _get_base_type(self, fd: FieldDescriptor) -> type:
        """
        Returns the Pydantic field type for the given FieldDescriptor.

        Parameters:
        -----------
        fd : FieldDescriptor
            The FieldDescriptor object to get the Pydantic field type for.

        Returns:
        --------
        type
            The Pydantic field type for the given FieldDescriptor.
        """
        pydantic_type = self.fields_map.get(fd.django_field_type.__name__)
        if not pydantic_type:
            logger.warning(f"Field {fd.django_field_type} is not supported")
            pydantic_type = Any
        return pydantic_type

    def _get_pydantic_field(
        self, fd: FieldDescriptor, base_type: type
    ) -> Tuple[type, Field]:
        """
        Returns a tuple containing the Pydantic type and field configuration for a given field descriptor and base type.

        Args:
            fd (FieldDescriptor): The field descriptor for the field.
            base_type (type): The base type of the field.

        Returns:
            Tuple[type, Field]: A tuple containing the Pydantic type and field configuration for the field.
        """
        pydantic_type = base_type
        if fd.choices:
            pydantic_type = Enum(
                f"{fd.name.title()}Enum",
                [(choice[1], choice[0]) for choice in fd.choices],
            )

        field_config = {}
        if fd.allows_null:
            pydantic_type = pydantic_type | None
            field_config["default"] = None
        if fd.default is not NOT_PROVIDED:
            if callable(fd.default):
                field_config.pop("default", None)
                field_config["default_factory"] = fd.default
            else:
                field_config["default"] = fd.default
        if issubclass(base_type, str):
            field_config["min_length"] = 0 if fd.allows_blank else 1
            if fd.max_length:
                field_config["max_length"] = fd.max_length
        return pydantic_type, Field(**field_config)

    def __call__(self, field: DjangoField, *, partial=False) -> Tuple[type, Field]:
        """
        Map a Django model field to a Pydantic field.

        Args:
            field (DjangoField): The Django model field to map.
            partial (bool): Whether the Pydantic field should allow partial updates.

        Returns:
            A tuple containing the Pydantic type and field that correspond to the Django field.
        """
        fd = self._get_field_descriptor(field, partial=partial)
        pydantic_type = self._get_base_type(fd)
        return self._get_pydantic_field(fd, pydantic_type)
