from enum import Enum, IntEnum, StrEnum
from typing import Annotated, Any

import pytest
from annotated_types import MaxLen, MinLen
from django.db import models
from pydantic.fields import FieldInfo

from pydref_serializers.serializers.field_mappers import (
    DJANGO_FIELD_MAP, _get_base_type, _get_enum_class,
    _get_pydantic_field_type, default_field_mapper)


class TestDefaultFieldMapper:
    def assert_field_annotation(self, field_info, annotation):
        field_ann = next(
            (ann for ann in field_info.metadata if isinstance(ann, type(annotation))),
            None,
        )
        assert field_ann == annotation

    def test__should_set_min_length_1_when_field_is_not_blank(
        self,
    ):
        field = models.CharField(blank=False)
        field_info: FieldInfo = default_field_mapper(field)[1]
        self.assert_field_annotation(field_info, MinLen(1))

    def test__should_set_min_length_0_when_field_is_blank(self):
        field = models.CharField(blank=True)
        field_info: FieldInfo = default_field_mapper(field)[1]
        self.assert_field_annotation(field_info, MinLen(0))

    def test__should_set_max_length_when_field_has_max_length(
        self,
    ):
        max_length = 100
        field = models.CharField(max_length=max_length)
        field_info: FieldInfo = default_field_mapper(field)[1]
        self.assert_field_annotation(field_info, MaxLen(max_length))


class TestGetFieldDefaultConfig:
    def test__should_set_default_when_field_has_default_value(
        self,
    ):
        default = "default"
        field = models.CharField(default=default)
        field_info: FieldInfo = default_field_mapper(field)[1]
        assert field_info.default == default

    def test__should_set_default_when_field_has_default_callable(
        self,
    ):
        default = "default"
        field = models.CharField(default=lambda: default)
        field_info: FieldInfo = default_field_mapper(field)[1]
        assert field_info.default_factory
        assert field_info.default_factory() == default


class TestGetPydanticField:
    @pytest.mark.parametrize(
        "django_field, expected_type",
        DJANGO_FIELD_MAP.items(),
        ids=lambda x: f"Testing {x} field",
    )
    def test__should_return_expected_type_when_field_is_supported(
        self, django_field, expected_type
    ):
        field = getattr(models, django_field)(max_length=100)
        pydantic_type = _get_pydantic_field_type(field)[0]
        assert pydantic_type == expected_type

    def test__should_return_any_when_field_is_not_supported(self):
        field = models.Field()
        pydantic_type = _get_pydantic_field_type(field)[0]
        assert pydantic_type == Any

    def test__should_return_type_or_none_when_field_is_nullable(self):
        field = models.Field(null=True)
        pydantic_type = default_field_mapper(field)[0]
        assert pydantic_type == Any | None

    def test__should_return_enum_when_field_has_choices(self):
        choices = (("a", "A"), ("b", "B"))
        field = models.CharField(choices=choices)
        field.name = "field"
        pydantic_type = _get_pydantic_field_type(field)[0]
        assert issubclass(pydantic_type, Enum)
        assert pydantic_type.__name__ == "FieldEnum"
        assert pydantic_type.__members__ == {
            "A": "a",
            "B": "b",
        }


class TestGetEnumClass:
    def test__should_return_int_enum_when_base_type_is_int_based(self):
        base_type = type("BaseInt", (int,), {})
        enum_class = _get_enum_class(base_type)
        assert issubclass(enum_class, IntEnum)

    def test__should_return_str_enum_when_base_type_is_str_based(self):
        base_type = type("BaseStr", (str,), {})
        enum_class = _get_enum_class(base_type)
        assert issubclass(enum_class, StrEnum)

    def test__should_return_enum_when_base_type_is_not_int_or_str_based(self):
        base_type = type("Base", (object,), {})
        enum_class = _get_enum_class(base_type)
        assert issubclass(enum_class, Enum)


class TestGetBaseType:
    def test__should_return_same_type_if_not_annotated(self):
        _type = type("Type", (object,), {})
        assert _get_base_type(_type) == _type

    def test__should_return_first_arg_if_type_is_annotated(self):
        _type = type("Type", (object,), {})
        annotated_type = Annotated[_type, "annotation"]
        assert _get_base_type(annotated_type) == _type
