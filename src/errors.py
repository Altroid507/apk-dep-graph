"""Domain-specific exceptions."""


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""


class PackageNotFoundError(Exception):
    """Raised when the requested package cannot be located."""


class RepositoryError(Exception):
    """Raised when the package repository cannot be accessed."""


class GraphFileError(Exception):
    """Raised when the local graph description file is malformed."""