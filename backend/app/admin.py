from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.db import engine
from app.models.organization import Organization
from app.models.profile import Patient
from app.models.user import User


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        # In a real app, we would verify Firebase session cookie here
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        # Placeholder: should check for valid admin session/token
        # For now, allow in local dev if needed or keep as is
        return True


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.is_active, User.is_superuser]
    column_searchable_list = [User.email]
    icon = "fa-solid fa-user"


class OrganizationAdmin(ModelView, model=Organization):
    column_list = [Organization.id, Organization.name, Organization.slug]
    column_searchable_list = [Organization.name, Organization.slug]
    icon = "fa-solid fa-building"


class PatientAdmin(ModelView, model=Patient):
    column_list = [Patient.id, Patient.user_id, Patient.mrn]
    column_searchable_list = [Patient.mrn]
    icon = "fa-solid fa-hospital-user"
    # Minimize PHI in list views
    column_details_exclude_list = [Patient.dob]


def setup_admin(app):
    authentication_backend = AdminAuth(secret_key="secret")  # Should be from settings
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(OrganizationAdmin)
    admin.add_view(PatientAdmin)
    return admin
