from pydref_serializers.serializers import ModelSerializerBuilder


class TestModelSerializerFromModel:
    def test_from_model__should_return_model_serializer_with_right_data(
        self, mocker, model_with_fields
    ):
        model_dict = {
            "char_field": "test",
            "int_field": 1,
            "bool_field": True,
        }

        TestModelSerializer = ModelSerializerBuilder.from_model_class(model_with_fields)

        model_serializer = TestModelSerializer.from_model(
            mocker.Mock(),
            model_to_dict=lambda obj: model_dict,
        )
        assert model_serializer.model_dump() == model_dict
