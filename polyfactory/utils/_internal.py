def is_attribute_overridden(base: type, cls: type, attribute_name: str) -> bool:
    for ancestor in cls.mro():
        if ancestor is base:
            return False

        if attribute_name in cls.__dict__:
            return True
    return False
