"""Domain exceptions — framework-agnostic business-rule failures.

Raised by service-layer functions. Mapped to HTTP status codes in api_errors.py.
AI agents should read `code` (stable) rather than parsing `message` (human-readable).
"""


class RetailDomainError(Exception):
    """Base for all retail business-rule violations."""

    code: str = "domain_error"

    def __init__(self, message: str, **context):
        super().__init__(message)
        self.message = message
        self.context = context


class RetailNotFoundError(RetailDomainError):
    """A requested RetailOps case or order does not exist."""

    code = "retail_not_found"


class RetailConflictError(RetailDomainError):
    """A command conflicts with the current RetailOps workflow state."""

    def __init__(self, code: str, message: str, **context):
        super().__init__(message, **context)
        self.code = code
