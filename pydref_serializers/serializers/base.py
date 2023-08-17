import logging
from typing import ClassVar, TypedDict

from django.db.models import Model as DjangoModel
from pydantic import BaseModel, create_model

from .getters import _FieldGetter, default_get_fields
from .mappers import _FieldMapper, default_field_mapper

logger = logging.getLogger(__name__)


class BaseSerializer(BaseModel):
    pass


class ConfigSerializerDict(TypedDict):
    model: type[DjangoModel]
    include_fields: list[str] | None
    exclude_fields: list[str] | None


class ModelSerializer(BaseSerializer):
    config: ClassVar[ConfigSerializerDict]


class ModelSerializerBuilder:
    @classmethod
    def from_model(
        cls,
        model: type[DjangoModel],
        *,
        fields_getter: _FieldGetter = default_get_fields,
        field_mapper: _FieldMapper = default_field_mapper,
    ) -> ModelSerializer:
        django_fields = fields_getter(model)
        pydantic_fields = {field.name: field_mapper(field) for field in django_fields}

        new_serializer = create_model(
            model.__name__ + "Serializer",
            __base__=ModelSerializer,
            config=ConfigSerializerDict(model=model),
            **pydantic_fields
        )
        return new_serializer
