from decimal import Decimal

from pydantic import BaseModel, condecimal

from pydantic_factories import FieldFactory, ModelFactory, SubFactory


def test_field_factory():
    class MyClass:
        name: str

        @classmethod
        def builder(cls, name: str) -> "MyClass":
            instance = MyClass()
            instance.name = name
            return instance

    default_name = "Moishe Zuchmir"

    class MyModel(BaseModel):
        my_class: MyClass

        class Config:
            arbitrary_types_allowed = True

    class MyFactory(ModelFactory):
        __model__ = MyModel
        my_class = FieldFactory(builder_fn=MyClass.builder, name=default_name)

    result = MyFactory.build()
    assert result.my_class.name == default_name


def test_sub_factory():
    default_name = "Moishe Zuchmir"

    class FirstModel(BaseModel):
        name: str

    class SecondModel(BaseModel):
        first_model: FirstModel

    class MyFactory(ModelFactory):
        __model__ = SecondModel
        first_model = SubFactory(model_factory=ModelFactory.create_dynamic_factory(FirstModel), name=default_name)

    result = MyFactory.build()
    assert result.first_model.name == default_name

def test_decimal():
    class Person(BaseModel):
        social_score: condecimal(decimal_places=3, max_digits=20, gt=Decimal(0))

    class PersonFactory(ModelFactory):
        __model__ = Person

    result = PersonFactory.build()
    assert isinstance(result.social_score, Decimal)
    assert len(str(result.social_score).split('.')[1]) == 3
    assert result.social_score > 0
