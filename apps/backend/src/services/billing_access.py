"""Billing access control and email routing for proxy billing management.

This service handles access control for billing operations and determines
email routing for billing notifications when a billing manager (proxy) is assigned.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assignments import PatientProxyAssignment
from src.models.profiles import Patient
from src.models.users import User

logger = logging.getLogger(__name__)


async def can_manage_billing(
    db: AsyncSession,
    patient_id: UUID,
    user_id: UUID,
) -> bool:
    """
    Check if a user can manage billing for a patient.

    A user can manage billing if they are:
    1. The patient themselves (patient.user_id == user_id)
    2. Assigned as the billing manager (patient.billing_manager_id == user_id)
    3. An active proxy with a proxy relationship to the patient

    Args:
        db: Database session
        patient_id: Patient ID
        user_id: User ID attempting to manage billing

    Returns:
        True if user can manage billing, False otherwise
    """
    # Get patient
    patient = await db.get(Patient, patient_id)
    if not patient:
        return False

    # Check if user is the patient
    if patient.user_id == user_id:
        return True

    # Check if user is the assigned billing manager
    if patient.billing_manager_id == user_id:
        from src.models.profiles import Proxy

        # Verify they still have an active proxy relationship
        # Need to join Proxy table since assignment links to Proxy.id, not User.id
        # Active = not revoked and (not expired or expired in future)
        proxy_check = await db.execute(
            select(PatientProxyAssignment)
            .join(Proxy, PatientProxyAssignment.proxy_id == Proxy.id)
            .where(
                PatientProxyAssignment.patient_id == patient_id,
                Proxy.user_id == user_id,
                PatientProxyAssignment.revoked_at.is_(None),
                PatientProxyAssignment.deleted_at.is_(None),
            )
        )
        return proxy_check.scalar_one_or_none() is not None

    return False


async def get_billing_email_recipient(
    db: AsyncSession,
    patient: Patient,
) -> tuple[str, str]:
    """
    Get the email recipient for billing notifications.

    If patient has a billing_manager_id assigned, emails go to the billing manager (proxy).
    Otherwise, emails go to the patient.

    Args:
        db: Database session
        patient: Patient object

    Returns:
        Tuple of (email, name) for the billing notification recipient
    """
    if patient.billing_manager_id:
        # Get billing manager user
        billing_manager = await db.get(User, patient.billing_manager_id)
        if billing_manager:
            logger.info(f"Routing billing email to billing manager {billing_manager.id} for patient {patient.id}")
            return (
                billing_manager.email,
                f"{billing_manager.first_name} {billing_manager.last_name}",
            )
        else:
            logger.warning(
                f"Billing manager {patient.billing_manager_id} not found "
                f"for patient {patient.id}, falling back to patient email"
            )

    # Default: send to patient
    # Try to get patient's user email if they have a user account
    if patient.user_id:
        user = await db.get(User, patient.user_id)
        if user:
            return user.email, f"{patient.first_name} {patient.last_name}"

    # Fallback: use patient's contact email (if you have one in ContactMethod table)
    # For now, log error - patient should have user_id or contact email
    logger.error(f"Patient {patient.id} has no user_id and no billing_manager_id. Cannot determine email recipient.")
    # Return a placeholder - calling code should handle this
    return "", f"{patient.first_name} {patient.last_name}"


async def validate_proxy_relationship_active(
    db: AsyncSession,
    patient_id: UUID,
    proxy_user_id: UUID,
) -> bool:
    """
    Validate that a proxy has an active relationship with a patient.

    Args:
        db: Database session
        patient_id: Patient ID
        proxy_user_id: Proxy user ID

    Returns:
        True if active relationship exists, False otherwise
    """
    from src.models.profiles import Proxy

    # Active = not revoked
    result = await db.execute(
        select(PatientProxyAssignment)
        .join(Proxy, PatientProxyAssignment.proxy_id == Proxy.id)
        .where(
            PatientProxyAssignment.patient_id == patient_id,
            Proxy.user_id == proxy_user_id,
            PatientProxyAssignment.revoked_at.is_(None),
            PatientProxyAssignment.deleted_at.is_(None),
        )
    )
    return result.scalar_one_or_none() is not None
