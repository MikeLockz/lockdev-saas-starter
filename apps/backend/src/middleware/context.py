from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Placeholder for future global context logic
        response = await call_next(request)
        return response
