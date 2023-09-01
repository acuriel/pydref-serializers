import logging
from typing import ClassVar, TypedDict

from django.db.models import Model as DjangoModel
from django.forms.models import model_to_dict as django_model_to_dict
from pydantic import BaseModel
from typing_extensions import Self

logger = logging.getLogger(__name__)


class BaseSerializer(BaseModel):
    """
    Base serializer class that all other serializers should inherit from.
    """

    pass


class ConfigSerializerDict(TypedDict):
    """
    A dictionary that represents the configuration for a Pydantic serializer.

    Attributes:
    -----------
    model : type[Model]
        The Django model to be serialized.
    fields : list[str] | None
        The list of fields to be included in the serialized output. If None, all fields will be included.
    """

    model: type[DjangoModel]
    fields: list[str] | None


class ModelSerializer(BaseSerializer):
    """
    A serializer that converts Django models to Pydantic models.

    Inherits from `BaseSerializer` and provides a `from_model` class method
    that takes a Django model instance and returns a Pydantic model instance
    with the same field values.

    :param config: A dictionary of configuration options for the serializer.
    """

    config: ClassVar[ConfigSerializerDict]

    @classmethod
    def from_model(
        cls: type[BaseModel], obj: DjangoModel, *, model_to_dict=django_model_to_dict
    ) -> Self:
        """
        Convert a Django model instance to a Pydantic model instance.

        Args:
            obj (DjangoModel): The Django model instance to convert.
            model_to_dict (Callable): A function that converts a Django model instance to a dictionary.

        Returns:
            Self: An instance of the Pydantic model class with the values from the Django model instance.
        """
        model_dict = model_to_dict(obj)
        return cls(**model_dict)
