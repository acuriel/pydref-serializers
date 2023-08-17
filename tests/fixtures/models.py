from pytest import fixture
from django.db import models

@fixture
def mocked_model(mocker) -> type:
    mocked_model = mocker.MagicMock(spec=models.Model, name="MockedModel")
    mocked_model = mocked_model.__class__
    mocked_model._meta = mocker.MagicMock()
    return mocked_model


@fixture
def empty_model(mocked_model) -> type:
    mocked_model._meta.fields = []
    return mocked_model


@fixture
def model_with_fields(mocked_model) -> type:
    mocked_model._meta.fields = [
        models.CharField(max_length=100),
        models.IntegerField(),
        models.BooleanField(),
    ]
    return mocked_model