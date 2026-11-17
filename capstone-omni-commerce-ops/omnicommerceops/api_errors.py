"""Map domain exceptions to HTTP responses."""

from fastapi import Request
from fastapi.responses import JSONResponse

from omnicommerceops.api_schemas import ApiErrorBody
from omnicommerceops.retail_exceptions import (
    RetailConflictError,
    RetailDomainError,
    RetailNotFoundError,
)

DOMAIN_ERROR_STATUS = {
    RetailNotFoundError: 404,
    RetailConflictError: 409,
}


async def handle_retail_domain_error(request: Request, exc: RetailDomainError):
    status_code = DOMAIN_ERROR_STATUS.get(type(exc), 400)
    return JSONResponse(
        status_code=status_code,
        content=ApiErrorBody(
            code=exc.code,
            message=exc.message,
            context=exc.context,
        ).model_dump(),
    )


def register_exception_handlers(app) -> None:
    app.add_exception_handler(RetailDomainError, handle_retail_domain_error)
