class FactoryExceptionError(Exception):
    """Base Factory error class"""


class ConfigurationExceptionError(FactoryExceptionError):
    """Configuration Error class - used for misconfiguration"""


class ParameterExceptionError(FactoryExceptionError):
    """Parameter exception - used when wrong parameters are used"""


class MissingBuildKwargExceptionError(FactoryExceptionError):
    """Missing Build Kwarg exception - used when a required build kwarg is not provided"""


class MissingDependencyExceptionError(FactoryExceptionError):
    """Missing dependency exception - used when a dependency is not installed"""
