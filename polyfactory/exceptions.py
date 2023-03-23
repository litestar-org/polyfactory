class FactoryError(Exception):
    """Base Factory error class"""


class ConfigurationError(FactoryError):
    """Configuration error - used for misconfiguration"""


class ParameterError(FactoryError):
    """Parameter error - used when wrong parameters are used"""


class MissingBuildKwargError(FactoryError):
    """Missing Build Kwarg error - used when a required build kwarg is not provided"""


class MissingDependencyError(FactoryError):
    """Missing Dependency error - used when a dependency is not installed"""
