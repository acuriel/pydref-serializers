from typing import Any
import pytest
from pydref_serializers.serializers.mappers import default_field_mapper, DJANGO_FIELD_MAP
from django.db import models


class TestDefaultFieldMapper:
    @pytest.mark.parametrize(
        "django_field, expected_type",
        DJANGO_FIELD_MAP.items(),
        ids=lambda x: f"Testing {x} field",
    )
    def test_default_field_mapper__should_return_expected_type_when_field_is_supported(self, django_field, expected_type):
        field = getattr(models, django_field)(max_length=100)
        pydantic_type = default_field_mapper(field)[0]
        assert pydantic_type == expected_type

    def test_default_field_mapper__should_return_any_when_field_is_not_supported(self):
        field = models.Field()
        pydantic_type = default_field_mapper(field)[0]
        assert pydantic_type == Any