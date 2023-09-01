import logging
from dataclasses import dataclass
from dataclasses import field as DataclassField

from django.db.models import Model as DjangoModel
from pydantic import create_model
from typing_extensions import Self, Set, Type

from .getters import _FieldGetter, default_get_fields
from .mappers.fields import FieldMapper, _FieldMapper
from .serializers import ConfigSerializerDict, ModelSerializer

logger = logging.getLogger(__name__)


@dataclass
class ModelSerializerBuilder:
    """
    A builder class for creating Pydantic ModelSerializer classes based on Django models.

    Attributes:
        model (Type[DjangoModel]): The Django model to create the serializer for.
        fields (Set[str] | None): The fields to include in the serialized output.
        fields_getter (_FieldGetter): A function that returns the fields to include in the serializer.
        field_mapper (_FieldMapper): A mapper that maps Django fields to Pydantic fields.
    """

    model: Type[DjangoModel]
    fields: Set[str] | None = None
    fields_getter: _FieldGetter = default_get_fields
    field_mapper: _FieldMapper = DataclassField(default_factory=FieldMapper)

    def with_fields(self, *field_names) -> Self:
        """
        Sets the fields to be included in the serialized output.

        Args:
            *field_names: A variable-length argument list of field names to include.

        Returns:
            Self: Returns the instance of the builder to allow for method chaining.

        Raises:
            ValueError: If both include and exclude fields are specified.
        """
        if self.fields is not None:
            raise ValueError("Cannot include and exclude fields at the same time")
        self.fields = set(field_names)
        return self

    def without_fields(self, *field_names) -> Self:
        """
        Returns a new instance of the builder with the specified fields excluded.

        Args:
            *field_names: The names of the fields to exclude.

        Returns:
            A new instance of the builder with the specified fields excluded.
        """
        if self.fields is not None:
            raise ValueError("Cannot include and exclude fields at the same time")
        self.fields = {field.name for field in self.fields_getter(self.model)}
        self.fields -= set(field_names)
        return self

    def build(self, partial=False) -> Type[ModelSerializer]:
        """
        Builds a new ModelSerializer class based on the provided Django model and fields.

        Args:
            partial (bool, optional): Whether to create a partial serializer. Defaults to False.

        Returns:
            Type[ModelSerializer]: The newly created ModelSerializer class.
        """
        django_fields = self.fields_getter(self.model, self.fields)
        pydantic_fields = {
            field.name: self.field_mapper(field, partial=partial)
            for field in django_fields
        }
        serializer_config = ConfigSerializerDict(
            model=self.model,
            fields=self.fields,
        )
        new_serializer = create_model(
            self.model.__name__ + "Serializer",
            __base__=ModelSerializer,
            config=serializer_config,
            **pydantic_fields,
        )
        return new_serializer

    @classmethod
    def from_model(
        cls,
        model: type[DjangoModel],
        /,
        *,
        fields_getter: _FieldGetter = default_get_fields,
        field_mapper: _FieldMapper = FieldMapper(),
    ) -> Self:
        """
        Create a new instance of the serializer builder from a Django model.

        Args:
            model (type[DjangoModel]): The Django model to create the serializer for.
            fields_getter (_FieldGetter, optional): A function that returns the fields to include in the serializer. Defaults to default_get_fields.
            field_mapper (_FieldMapper, optional): A mapper that maps Django fields to Pydantic fields. Defaults to FieldMapper().

        Returns:
            Self: A new instance of the serializer builder.
        """
        return cls(model, fields_getter=fields_getter, field_mapper=field_mapper)
