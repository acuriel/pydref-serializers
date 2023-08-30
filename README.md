# PyDReF - Serializers

## Description
This library contains a set of tools to help you create simple serializers for Django models. It was inspired by the [Django REST Framework](https://www.django-rest-framework.org/) and [Pydantic](https://pydantic.dev/) projects.

## Motivation
The main motivation for creating this library was to have a simple and easy to use tool to serialize Django models. The library is designed to be used in projects where you need to serialize Django models, but you don't want to use the Django REST Framework.

DRF is a great tool, but it is not always necessary to use it. For example, if you need to create a simple API for a small project, you can use this library instead of the DRFfor the serialization of your models.

Also, though DRF is a great tool, I've never enjoy the heavy responsibility added to its Serializers. Pydantic keeps this simplicity, where the serializers (Pydantic models) are just a simple class that you can use to serialize your data.

## Installation
You can install this library using pip:
```bash
pip install pydref-serializers
```

## Usage

### Creating a serializer class
For creating a serializer for a Django model, you can use the `ModelSerializerBuilder` class. This class will create a Pydantic model based on the Django model that you pass to it.

```python
from pydref_serializers import ModelSerializerBuilder
from myapp.models import MyModel

MyModelSerializer = ModelSerializerBuilder.from_model_class(MyModel)
```

The builder will return a class created based on the specified model. If you want to set the fields to be added to the serializer, you can specify them during the creation of the serializer, using the kwargs `include_fields` or `exclude_fields`:

```python
from pydref_serializers import ModelSerializerBuilder
from myapp.models import MyModel

MyModelSerializer = ModelSerializerBuilder.from_model_class(
    MyModel,
    include_fields=['field1', 'field2', 'field3'],
    # exclude_fields=['field1', 'field2', 'field3'],
)
```

The `ModelSerializerBuilder` also has a few kwargs for configuration how the builder get the fields from the Django model, and also how it maps the fields to the Pydantic model fields.

```python
from pydref_serializers import ModelSerializerBuilder
from myapp.models import MyModel


_FieldMapper = Callable[[DjangoField], tuple[type, Any]]
_FieldGetter = Callable[[type[DjangoModel], Collection[str] | None, Collection[str] | None], dict[type, Any]]

MyModelSerializer = ModelSerializerBuilder.from_model_class(
    MyModel,
    ..., # include_fields or exclude_fields
    fields_getter:_FieldGetter = ...,
    field_mapper:_FieldMapper = ...,
)
```

### Using the serializer

For using the serializer, you can use it as a normal Pydantic model, passing the fields to be serialized as kwargs to the constructor:

```python
from myapp.serializers import MyModelSerializer

serializer = MyModelSerializer(
    field1='value1',
    field2='value2',
    field3='value3',
)
```

The serializer will validate the fields based on the validators created during the Django Fields to Pydantic annotations mapping.

You can also use the serializer to serialize a Django model instance:

```python
from myapp.serializers import MyModelSerializer
from myapp.models import MyModel

my_model_instance = MyModel.objects.get(pk=1)
serializer = MyModelSerializer.from_model(my_model_instance)
```

The class method `from_model` will create a serializer instance based on the Django model instance passed to it. It will convert the model to dict using the django utility `model_to_dict` located at `django.forms.models`, and then it will pass the dict to the serializer constructor. You can change this behavior passing a custom function to the `model_to_dict` kwarg of the `from_model` method:

```python
from myapp.serializers import MyModelSerializer
from myapp.models import MyModel

my_model_instance = MyModel.objects.get(pk=1)
serializer = MyModelSerializer.from_model(
    my_model_instance,
    model_to_dict=lambda model_instance: model_instance.to_dict(),
)
```

### Field mapping

Fields are transformed based on the following rules:

* Field types are mapped from Django Field to Pydantic annotations based on the dictionary below:

```python
DJANGO_FIELD_MAP = {
    # Numerical related fields
    "AutoField": int,
    "BigAutoField": int,
    "IntegerField": int,
    "SmallIntegerField": int,
    "BigIntegerField": int,
    "PositiveIntegerField": PositiveInt,
    "PositiveSmallIntegerField": PositiveInt,
    "FloatField": float,
    "DecimalField": Decimal,
    # String related fields
    "CharField": str,
    "TextField": str,
    "SlugField": str,
    "EmailField": EmailStr,
    "URLField": AnyUrl,
    "FilePathField": FilePath,
    "FileField": FilePath,
    "ImageField": FilePath,
    # Other built-in fields
    "BooleanField": bool,
    "BinaryField": bytes,
    "DateField": date,
    "DateTimeField": datetime,
    "DurationField": timedelta,
    "TimeField": time,
    "UUIDField": UUID,
    "GenericIPAddressField": IPvAnyAddress,
    "JSONField": Json,
}
```

* If Django field `max_length` is set, the Pydantic field will also be set with `max_length` equal to the Django field `max_length`.
* If Django field has `blank=True`, the Pydantic field will have `min_length=0`.
* If Django field has `blank=False`, the Pydantic field will have `min_length=1`.
* If Django field has `null=True`, the Pydantic field will have `field_type | None`.
* If Django field has `default` value set, the Pydantic field will have `default` set to the Django field `default`. In case this value is a callable, it will be used for the pydantic field `default_factory`.
* If Django field has `choices` set, the Pydantic field will sue as a type an created Enum based on the specified `choices` set to the Django field. If the field is int based, the Enum will be an IntEnum. If the field is str based, the Enum will be StrEnum, otherwise it will be an Enum.

## TODO
* Add support for lower Python versions (3.6+).
* Add support for Django model relations.
* Add support for Django model inheritance.
* Add support for Django model fields with custom validators.
* Add support to customize the serializer fields.
* Add support to serialize model properties.
