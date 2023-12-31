from pydref_serializers.getters import default_get_fields


class TestDefaultGetFields:
    def test_get_fields__should_return_all_fields_when_model_contains_fields(
        self, model_with_fields
    ):
        expected = model_with_fields._meta.fields
        actual = default_get_fields(model_with_fields)
        assert actual == expected

    def test_get_fields__should_return_empty_list_when_model_does_not_contain_fields(
        self, empty_model
    ):
        expected = []
        actual = default_get_fields(empty_model)
        assert actual == expected

    def test_get_fields__should_return_expected_fields_when_include_is_provided(
        self, model_with_fields
    ):
        included = model_with_fields._meta.fields[0]
        actual = default_get_fields(model_with_fields, fields=[included.name])
        assert actual == [included]
