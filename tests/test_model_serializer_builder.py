import pytest

from pydref_serializers.builders import ModelSerializerBuilder
from pydref_serializers.serializers import ModelSerializer


class TestModelSerializerBuilderBuild:
    def test_build__should_create_model_serializer_when_empty_model_provided(
        self, empty_model
    ):
        serializer_class = ModelSerializerBuilder(
            model=empty_model, fields_getter=lambda model, *args, **kwargs: []
        ).build()
        assert issubclass(serializer_class, ModelSerializer)


class TestModelSerializerBuilderWithFields:
    def test_with_fields__raise_value_error_when_fields_already_set(self, empty_model):
        with pytest.raises(ValueError):
            ModelSerializerBuilder(model=empty_model, fields={"field"}).with_fields(
                "field"
            )

    def test_with_fields__should_set_fields_when_provided(self, empty_model):
        builder = ModelSerializerBuilder(model=empty_model).with_fields("field")
        assert builder.fields == {"field"}

    def test_with_fields__should_return_self(self, empty_model):
        builder = ModelSerializerBuilder(model=empty_model)
        assert builder.with_fields("field") is builder


class TestModelSerializerBuilderWithoutFields:
    def test_without_fields__raise_value_error_when_fields_already_set(
        self, empty_model
    ):
        with pytest.raises(ValueError):
            ModelSerializerBuilder(model=empty_model, fields={"field"}).without_fields(
                "field"
            )

    def test_without_fields__should_set_fields_when_provided(self, model_with_fields):
        builder = ModelSerializerBuilder(
            model=model_with_fields,
        ).without_fields("char_field")
        assert "char_field" not in builder.fields

    def test_without_fields__should_return_self(self, empty_model):
        builder = ModelSerializerBuilder(model=empty_model)
        assert builder.without_fields("field") is builder


class TestModelSerializerBuilderFromModel:
    def test_from_model__should_create_builder_with_model(self, empty_model):
        builder = ModelSerializerBuilder.from_model(empty_model)
        assert builder.model is empty_model
        assert isinstance(builder, ModelSerializerBuilder)
