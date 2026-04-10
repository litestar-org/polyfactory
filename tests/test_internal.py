from polyfactory.utils._internal import is_attribute_overridden


class BaseClass:
    base_attr = "base_value"


class ChildClass(BaseClass):
    base_attr = "child_value"


class GrandChildClass(ChildClass):
    pass


class NonOverriddenClass(BaseClass):
    """A class that does not override the base attribute."""


def test_is_attribute_overridden() -> None:
    """Test the is_attribute_overridden function."""
    assert is_attribute_overridden(BaseClass, ChildClass, "base_attr")
    assert is_attribute_overridden(BaseClass, GrandChildClass, "base_attr")


def test_is_attribute_not_overridden() -> None:
    assert not is_attribute_overridden(BaseClass, NonOverriddenClass, "base_attr")
