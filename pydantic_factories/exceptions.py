class ModelFactoryError(Exception):
    pass


class ConfigurationError(ModelFactoryError):
    pass


class ParameterError(ModelFactoryError):
    pass


class MissingBuildKwargError(ModelFactoryError):
    pass
