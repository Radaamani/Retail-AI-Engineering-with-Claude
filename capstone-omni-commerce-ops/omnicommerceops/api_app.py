"""FastAPI application assembly — wires routes, dependencies, and error handlers."""

from fastapi import FastAPI

from omnicommerceops.api_dependencies import lifespan
from omnicommerceops.api_errors import register_exception_handlers
from omnicommerceops.api_routes import router

app = FastAPI(title="RetailOps API", version="1.0.0", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(router)
