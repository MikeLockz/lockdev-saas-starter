"""
Care Team Service

Business logic for managing provider-patient care team relationships.

IMPORTANT: This module enforces the "One Primary Provider" business rule.
See migration: 20260114_add_unique_primary_provider_constraint.py
"""
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# NOTE: Import your actual models when they're created
# from src.models import CareTeamAssignment


class DuplicatePrimaryProviderError(Exception):
    """Raised when attempting to assign a second primary provider."""
    pass


class CareTeamService:
    """
    Service for managing care team assignments.

    Business Rules:
    - Each patient can have multiple providers on their care team
    - Only ONE provider can be marked as "primary" per patient per organization
    - The primary provider is the main point of accountability for patient care
    """

    @staticmethod
    async def assign_primary_provider(
        db: AsyncSession,
        organization_id: UUID,
        patient_id: UUID,
        provider_id: UUID
    ) -> None:
        """
        Assign a provider as the primary for a patient.

        This method automatically demotes any existing primary provider
        before assigning the new one, ensuring atomicity.

        Args:
            db: Database session
            organization_id: The organization/tenant ID
            patient_id: The patient's ID
            provider_id: The provider to make primary

        Raises:
            IntegrityError: If database constraint is violated (defensive check)

        Example:
            await CareTeamService.assign_primary_provider(
                db=session,
                organization_id=clinic_id,
                patient_id=patient.id,
                provider_id=new_doctor.id
            )
        """
        # STEP 1: Demote existing primary provider (if any)
        # This prevents constraint violation by ensuring only one assignment
        # will have is_primary_provider=TRUE at a time
        await db.execute(
            update(CareTeamAssignment)
            .where(
                CareTeamAssignment.organization_id == organization_id,
                CareTeamAssignment.patient_id == patient_id,
                CareTeamAssignment.is_primary_provider == True
            )
            .values(is_primary_provider=False)
        )

        # STEP 2: Promote the specified provider to primary
        # Check if this provider is already on the care team
        stmt = select(CareTeamAssignment).where(
            CareTeamAssignment.organization_id == organization_id,
            CareTeamAssignment.patient_id == patient_id,
            CareTeamAssignment.provider_id == provider_id
        )
        existing_assignment = await db.scalar(stmt)

        if existing_assignment:
            # Update existing assignment
            existing_assignment.is_primary_provider = True
        else:
            # Create new assignment
            new_assignment = CareTeamAssignment(
                organization_id=organization_id,
                patient_id=patient_id,
                provider_id=provider_id,
                is_primary_provider=True
            )
            db.add(new_assignment)

        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            # This should not happen if the demote logic above works correctly
            # But we catch it defensively
            if 'idx_unique_primary_provider_per_patient' in str(e):
                raise DuplicatePrimaryProviderError(
                    f"Patient {patient_id} already has a primary provider in organization {organization_id}"
                ) from e
            raise

    @staticmethod
    async def add_secondary_provider(
        db: AsyncSession,
        organization_id: UUID,
        patient_id: UUID,
        provider_id: UUID
    ) -> None:
        """
        Add a provider to the care team as a secondary/consulting provider.

        Unlike assign_primary_provider, this does NOT change existing primary.
        Multiple secondary providers are allowed.

        Args:
            db: Database session
            organization_id: The organization/tenant ID
            patient_id: The patient's ID
            provider_id: The provider to add as secondary

        Example:
            # Add a specialist as secondary provider
            await CareTeamService.add_secondary_provider(
                db=session,
                organization_id=clinic_id,
                patient_id=patient.id,
                provider_id=specialist.id
            )
        """
        # Check if provider is already on the team
        stmt = select(CareTeamAssignment).where(
            CareTeamAssignment.organization_id == organization_id,
            CareTeamAssignment.patient_id == patient_id,
            CareTeamAssignment.provider_id == provider_id
        )
        existing = await db.scalar(stmt)

        if not existing:
            new_assignment = CareTeamAssignment(
                organization_id=organization_id,
                patient_id=patient_id,
                provider_id=provider_id,
                is_primary_provider=False  # Explicitly set to False
            )
            db.add(new_assignment)
            await db.commit()

    @staticmethod
    async def get_primary_provider(
        db: AsyncSession,
        organization_id: UUID,
        patient_id: UUID
    ) -> UUID | None:
        """
        Get the primary provider ID for a patient.

        Returns:
            Provider UUID if primary exists, None otherwise

        Example:
            primary_id = await CareTeamService.get_primary_provider(
                db=session,
                organization_id=clinic_id,
                patient_id=patient.id
            )
        """
        stmt = select(CareTeamAssignment.provider_id).where(
            CareTeamAssignment.organization_id == organization_id,
            CareTeamAssignment.patient_id == patient_id,
            CareTeamAssignment.is_primary_provider == True
        )
        result = await db.scalar(stmt)
        return result

    @staticmethod
    async def remove_from_care_team(
        db: AsyncSession,
        organization_id: UUID,
        patient_id: UUID,
        provider_id: UUID
    ) -> bool:
        """
        Remove a provider from a patient's care team.

        WARNING: If removing the primary provider, you should assign a new
        primary provider first to maintain care continuity.

        Returns:
            True if provider was removed, False if not found

        Example:
            # First assign new primary
            await CareTeamService.assign_primary_provider(db, org, patient, new_primary)
            # Then remove old provider
            await CareTeamService.remove_from_care_team(db, org, patient, old_provider)
        """
        stmt = select(CareTeamAssignment).where(
            CareTeamAssignment.organization_id == organization_id,
            CareTeamAssignment.patient_id == patient_id,
            CareTeamAssignment.provider_id == provider_id
        )
        assignment = await db.scalar(stmt)

        if assignment:
            await db.delete(assignment)
            await db.commit()
            return True
        return False
