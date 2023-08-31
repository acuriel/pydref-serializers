import logging
from dataclasses import dataclass

from django.db.models import Model as DjangoModel
from pydantic import create_model
from typing_extensions import Self, Set

from .getters import _FieldGetter, default_get_fields
from .mappers.fields import _FieldMapper, default_field_mapper
from .serializers import ConfigSerializerDict, ModelSerializer

logger = logging.getLogger(__name__)


@dataclass
class ModelSerializerBuilder:
    model: type[DjangoModel]
    fields: Set[str] | None = None
    fields_getter: _FieldGetter = default_get_fields
    field_mapper: _FieldMapper = default_field_mapper

    def with_fields(self, *field_names) -> Self:
        if self.fields is not None:
            raise ValueError("Cannot include and exclude fields at the same time")
        self.fields = set(field_names)
        return self

    def without_fields(self, *field_names) -> Self:
        if self.fields is not None:
            raise ValueError("Cannot include and exclude fields at the same time")
        self.fields = {field.name for field in self.fields_getter(self.model)}
        self.fields -= set(field_names)
        return self

    def build(self, partial=False) -> type(ModelSerializer):
        django_fields = self.fields_getter(self.model, self.fields)
        pydantic_fields = {
            field.name: self.field_mapper(field) for field in django_fields
        }
        serializer_config = ConfigSerializerDict(
            model=self.model,
            include_fields=self.fields,
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
        field_mapper: _FieldMapper = default_field_mapper,
    ) -> Self:
        return cls(model, fields_getter=fields_getter, field_mapper=field_mapper)
