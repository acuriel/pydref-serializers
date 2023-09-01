from enum import Enum
from typing import Any

import pytest
from annotated_types import MaxLen, MinLen
from django.db import models
from pydantic.fields import FieldInfo

from pydref_serializers.mappers.fields import (
    DJANGO_FIELD_MAP,
    FieldDescriptor,
    FieldMapper,
)


def assert_field_annotation(field_info: FieldInfo, annotation):
    field_ann = next(
        (ann for ann in field_info.metadata if isinstance(ann, type(annotation))),
        None,
    )
    assert field_ann == annotation


class TestFieldMapperGetFieldDescriptor:
    def test__should_return_field_descriptor_with_basic_fields(self):
        field = models.CharField(null=True, choices=(("a", "A"), ("b", "B")))
        fd = FieldMapper()._get_field_descriptor(field)
        assert fd.name == field.name
        assert fd.django_field_type == field.__class__
        assert fd.allows_null == field.null
        assert fd.choices == field.choices

    def test__should_return_field_descriptor_with_is_required_false_when_field_is_nullable(
        self,
    ):
        field = models.CharField(null=True)
        fd = FieldMapper()._get_field_descriptor(field)
        assert fd.is_required is False

    def test__should_return_field_descriptor_with_is_required_false_when_field_is_partial(
        self,
    ):
        field = models.CharField()
        fd = FieldMapper()._get_field_descriptor(field, partial=True)
        assert fd.is_required is False

    def test__should_return_field_descriptor_with_is_required_false_when_field_has_default(
        self,
    ):
        field = models.CharField(default="default")
        fd = FieldMapper()._get_field_descriptor(field)
        assert fd.is_required is False

    def test__should_set_default_to_value_if_default_is_provided(self):
        default = "default"
        field = models.CharField(default=default)
        fd = FieldMapper()._get_field_descriptor(field)
        assert fd.default == default

    def test__should_set_default_to_callable_if_default_is_callable(self):
        default = "default"

        def default_callable():
            return default

        field = models.CharField(default=default_callable)
        fd = FieldMapper()._get_field_descriptor(field)
        assert callable(fd.default)
        assert fd.default() == default


class TestFieldMapperGetBaseType:
    @pytest.mark.parametrize(
        "django_field, expected_type",
        DJANGO_FIELD_MAP.items(),
        ids=lambda x: f"Testing {x} field",
    )
    def test__should_return_expected_type_when_field_is_supported(
        self, django_field, expected_type
    ):
        field_type = getattr(models, django_field)
        fd = FieldDescriptor(django_field_type=field_type, name="field")
        pydantic_type = FieldMapper()._get_base_type(fd)
        assert pydantic_type == expected_type

    def test__should_return_any_when_field_is_not_supported(self):
        fd = FieldDescriptor(django_field_type=object, name="field")
        pydantic_type = FieldMapper()._get_base_type(fd)
        assert pydantic_type == Any


class TestFieldMapperGetPydanticField:
    def test__should_return_type_or_none_when_fd_allows_null(self):
        fd = FieldDescriptor(
            name="field", django_field_type=models.CharField, allows_null=True
        )
        pydantic_type = FieldMapper()._get_pydantic_field(fd, str)[0]
        assert pydantic_type == str | None

    def test__should_return_enum_when_field_has_choices(self):
        choices = (("a", "A"), ("b", "B"))
        fd = FieldDescriptor(
            django_field_type=models.CharField, name="field", choices=choices
        )
        pydantic_type = FieldMapper()._get_pydantic_field(fd, str)[0]
        assert issubclass(pydantic_type, Enum)
        assert pydantic_type.__name__ == "FieldEnum"

    def test__should_set_default_none_when_fd_allows_null_and_not_default_provided(
        self,
    ):
        fd = FieldDescriptor(
            name="field", django_field_type=models.CharField, allows_null=True
        )
        field_info:FieldInfo = FieldMapper()._get_pydantic_field(fd, str)[1]
        assert field_info.default is None

    def test__should_set_default_when_field_default_is_not_callable(self):
        default = "default"
        fd = FieldDescriptor(
            django_field_type=models.CharField, name="field", default=default
        )
        field_info = FieldMapper()._get_pydantic_field(fd, str)[1]
        assert field_info.default == default

    def test__should_set_default_when_field_default_is_callable(self):
        default = "default"

        def default_callable():
            return default

        fd = FieldDescriptor(
            django_field_type=models.CharField, name="field", default=default_callable
        )
        field_info = FieldMapper()._get_pydantic_field(fd, str)[1]
        assert field_info.default_factory
        assert field_info.default_factory() == default

    def test__should_set_min_length_1_when_field_is_not_blank(self):
        fd = FieldDescriptor(
            django_field_type=models.CharField, name="field", allows_blank=False
        )
        field_info = FieldMapper()._get_pydantic_field(fd, str)[1]
        assert_field_annotation(field_info, MinLen(1))

    def test__should_set_min_length_0_when_field_is_blank(self):
        fd = FieldDescriptor(
            django_field_type=models.CharField, name="field", allows_blank=True
        )
        field_info = FieldMapper()._get_pydantic_field(fd, str)[1]
        assert_field_annotation(field_info, MinLen(0))

    def test__should_set_max_length_when_field_has_max_length(self):
        max_length = 100
        fd = FieldDescriptor(
            django_field_type=models.CharField, name="field", max_length=max_length
        )
        field_info = FieldMapper()._get_pydantic_field(fd, str)[1]
        assert_field_annotation(field_info, MaxLen(max_length))
