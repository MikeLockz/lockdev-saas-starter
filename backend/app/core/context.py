from contextvars import ContextVar

current_user_id: ContextVar[str | None] = ContextVar("current_user_id", default=None)
current_tenant_id: ContextVar[str | None] = ContextVar(
    "current_tenant_id", default=None
)
