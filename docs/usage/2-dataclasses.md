# Supported Models

This library works with any class that inherits the pydantic `BaseModel` class, including `GenericModel` and classes
from 3rd party libraries, and also with dataclasses - both those from the python standard library and pydantic's
dataclasses. Finally, it also supports `TypedDict` classes. In fact, you can use them interchangeably as you like:

```python
import dataclasses
from typing import Dict, List

import pydantic
from polyfactory.factories.pydantic_factory import ModelFactory


@pydantic.dataclasses.dataclass
class MyPydanticDataClass:
    name: str


class MyFirstModel(pydantic.BaseModel):
    dataclass: MyPydanticDataClass


@dataclasses.dataclass()
class MyPythonDataClass:
    id: str
    complex_type: Dict[str, Dict[int, List[MyFirstModel]]]


class MySecondModel(pydantic.BaseModel):
    dataclasses: List[MyPythonDataClass]


class MyFactory(ModelFactory):
    __model__ = MySecondModel


result = MyFactory.build()
```

The above example will build correctly.

## Note Regarding Nested Optional Types in Dataclasses

When generating mock values for fields typed as `Optional`, if the factory is defined
with `__allow_none_optionals__ = True`, the field value will be either a value or None - depending on a random decision.
This works even when the `Optional` typing is deeply nested, except for dataclasses - typing is only shallowly evaluated
for dataclasses, and as such they are always assumed to require a value. If you wish to have a None value, in this
particular case, you should do so manually by configured a `Use` callback for the particular field.
