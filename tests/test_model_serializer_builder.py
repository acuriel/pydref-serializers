from pydref_serializers.serializers import ModelSerializer, ModelSerializerBuilder


class TestFromModel:
    def test_from_model__should_create_model_serializer_when_empty_model_provided(
        self, empty_model
    ):
        serializer_class = ModelSerializerBuilder.from_model_class(
            model=empty_model,
            fields_getter=lambda model: [],
        )
        assert issubclass(serializer_class, ModelSerializer)
