import logging
from typing import ClassVar, Collection, TypedDict

from django.db.models import Model as DjangoModel
from django.forms.models import model_to_dict as django_model_to_dict
from pydantic import BaseModel, create_model
from typing_extensions import Self

from .field_mappers import _FieldMapper, default_field_mapper
from .getters import _FieldGetter, default_get_fields

logger = logging.getLogger(__name__)


class BaseSerializer(BaseModel):
    pass


class ConfigSerializerDict(TypedDict):
    model: type[DjangoModel]
    include_fields: list[str] | None
    exclude_fields: list[str] | None


class ModelSerializer(BaseSerializer):
    config: ClassVar[ConfigSerializerDict]

    @classmethod
    def from_model(
        cls: type[BaseModel], obj: DjangoModel, *, model_to_dict=django_model_to_dict
    ) -> Self:
        model_dict = model_to_dict(obj)
        return cls(**model_dict)


class ModelSerializerBuilder:
    @classmethod
    def from_model_class(
        cls,
        model: type[DjangoModel],
        *,
        include_fields: Collection[str] = None,
        exclude_fields: Collection[str] = None,
        fields_getter: _FieldGetter = default_get_fields,
        field_mapper: _FieldMapper = default_field_mapper,
    ) -> ModelSerializer:
        django_fields = fields_getter(
            model, include_fields=include_fields, exclude_fields=exclude_fields
        )
        pydantic_fields = {field.name: field_mapper(field) for field in django_fields}
        serializer_config = ConfigSerializerDict(
            model=model,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
        )
        new_serializer = create_model(
            model.__name__ + "Serializer",
            __base__=ModelSerializer,
            config=serializer_config,
            **pydantic_fields,
        )
        return new_serializer
