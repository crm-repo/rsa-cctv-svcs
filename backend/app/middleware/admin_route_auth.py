"""Admin route authentication middleware for RSA CMS / Mini-CRM.

Batch 46 protects admin/CRM management API surfaces at the backend layer.
Nginx may expose these routes, but anonymous requests must still receive 401.

Public exceptions:
- /api/admin/auth/* remains public-safe for login/config/status.
- POST /api/bookings and POST /api/inquiries remain public form submissions.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.admin_auth import get_admin_auth_config, get_optional_admin_user


PUBLIC_ADMIN_AUTH_PREFIX = "/api/admin/auth/"
PUBLIC_FORM_CREATE_PATHS = {"/api/bookings", "/api/inquiries"}
PROTECTED_PREFIXES = (
    "/api/admin/",
    "/api/customers",
    "/api/customers/",
    "/api/bookings",
    "/api/bookings/",
    "/api/inquiries",
    "/api/inquiries/",
)


def _normalize_path(path: str) -> str:
    if not path:
        return "/"
    return path if path.startswith("/") else f"/{path}"


def route_requires_admin(path: str, method: str) -> bool:
    """Return True when a request path should require admin auth."""

    normalized_path = _normalize_path(path)
    request_method = (method or "GET").upper()

    # Admin login/config/status endpoints are intentionally public-safe.
    if normalized_path.startswith(PUBLIC_ADMIN_AUTH_PREFIX):
        return False

    # Public website forms must remain usable without admin login.
    if request_method == "POST" and normalized_path.rstrip("/") in PUBLIC_FORM_CREATE_PATHS:
        return False

    return normalized_path.startswith(PROTECTED_PREFIXES)


class AdminRouteAuthMiddleware(BaseHTTPMiddleware):
    """Require a valid admin bearer token for admin/CRM management APIs."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not route_requires_admin(request.url.path, request.method):
            return await call_next(request)

        config = get_admin_auth_config()
        # Preserve local preview behavior when auth is intentionally disabled.
        if not config.get("admin_routes_protected"):
            return await call_next(request)

        authorization = request.headers.get("authorization")
        user = get_optional_admin_user(authorization=authorization)
        if user is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Admin authentication required."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.admin_user = user
        return await call_next(request)
