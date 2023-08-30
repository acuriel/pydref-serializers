import logging
from typing import ClassVar, TypedDict

from django.db.models import Model as DjangoModel
from django.forms.models import model_to_dict as django_model_to_dict
from pydantic import BaseModel
from typing_extensions import Self

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
