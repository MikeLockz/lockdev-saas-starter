"""
Test suite for Primary Provider Constraint

Tests verify that the database constraint and service layer properly enforce:
"Only ONE provider can be marked as primary per patient per organization"

Related:
- Migration: 20260114_add_unique_primary_provider_constraint.py
- Service: src/services/care_team_service.py
- Constraint: idx_unique_primary_provider_per_patient
"""
import pytest
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# NOTE: Update these imports when models are created
# from src.models import CareTeamAssignment, Organization, Patient, Provider
# from src.services.care_team_service import CareTeamService, DuplicatePrimaryProviderError


@pytest.mark.asyncio
class TestPrimaryProviderConstraint:
    """Test database-level constraint enforcement."""

    async def test_one_primary_provider_per_patient(self, db_session):
        """
        Test that database prevents multiple primary providers for same patient.

        CRITICAL: This test verifies the partial unique index works correctly.
        """
        org_id = uuid4()
        patient_id = uuid4()
        provider1_id = uuid4()
        provider2_id = uuid4()

        # Create first primary provider - should succeed
        assignment1 = CareTeamAssignment(
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=provider1_id,
            is_primary_provider=True
        )
        db_session.add(assignment1)
        await db_session.commit()

        # Verify it was created
        result = await db_session.execute(
            select(CareTeamAssignment).where(
                CareTeamAssignment.patient_id == patient_id,
                CareTeamAssignment.is_primary_provider == True
            )
        )
        primaries = result.scalars().all()
        assert len(primaries) == 1, "Should have exactly one primary provider"

        # Attempt to create second primary provider - should FAIL
        assignment2 = CareTeamAssignment(
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=provider2_id,
            is_primary_provider=True  # This violates the constraint
        )
        db_session.add(assignment2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        # Verify the specific constraint was violated
        assert 'idx_unique_primary_provider_per_patient' in str(exc_info.value)

    async def test_multiple_non_primary_providers_allowed(self, db_session):
        """
        Test that multiple NON-primary providers are allowed.

        The constraint should only apply when is_primary_provider=TRUE.
        """
        org_id = uuid4()
        patient_id = uuid4()

        # Create multiple non-primary providers - should all succeed
        provider_ids = [uuid4() for _ in range(5)]
        for provider_id in provider_ids:
            assignment = CareTeamAssignment(
                organization_id=org_id,
                patient_id=patient_id,
                provider_id=provider_id,
                is_primary_provider=False  # All are secondary
            )
            db_session.add(assignment)

        await db_session.commit()  # Should not raise

        # Verify all were created
        result = await db_session.execute(
            select(CareTeamAssignment).where(
                CareTeamAssignment.patient_id == patient_id
            )
        )
        assignments = result.scalars().all()
        assert len(assignments) == 5, "Should have all 5 secondary providers"

    async def test_different_patients_can_have_same_primary_provider(self, db_session):
        """
        Test that the SAME provider can be primary for DIFFERENT patients.

        The constraint is per (org, patient), not per provider.
        """
        org_id = uuid4()
        provider_id = uuid4()  # Same provider
        patient1_id = uuid4()
        patient2_id = uuid4()

        # Assign same provider as primary for patient 1
        assignment1 = CareTeamAssignment(
            organization_id=org_id,
            patient_id=patient1_id,
            provider_id=provider_id,
            is_primary_provider=True
        )
        db_session.add(assignment1)
        await db_session.commit()

        # Assign same provider as primary for patient 2 - should succeed
        assignment2 = CareTeamAssignment(
            organization_id=org_id,
            patient_id=patient2_id,
            provider_id=provider_id,
            is_primary_provider=True
        )
        db_session.add(assignment2)
        await db_session.commit()  # Should not raise

    async def test_different_orgs_can_have_different_primaries(self, db_session):
        """
        Test that same patient can have different primary providers in different orgs.

        Multi-tenancy: Patient sees Dr. Smith at Clinic A, Dr. Jones at Clinic B.
        """
        patient_id = uuid4()  # Same patient
        org1_id = uuid4()
        org2_id = uuid4()
        provider1_id = uuid4()
        provider2_id = uuid4()

        # Primary at Clinic A
        assignment1 = CareTeamAssignment(
            organization_id=org1_id,
            patient_id=patient_id,
            provider_id=provider1_id,
            is_primary_provider=True
        )
        db_session.add(assignment1)
        await db_session.commit()

        # Primary at Clinic B - should succeed (different org)
        assignment2 = CareTeamAssignment(
            organization_id=org2_id,
            patient_id=patient_id,
            provider_id=provider2_id,
            is_primary_provider=True
        )
        db_session.add(assignment2)
        await db_session.commit()  # Should not raise

    async def test_can_change_primary_by_updating_existing(self, db_session):
        """
        Test that primary can be changed by updating the boolean flag.

        This is the safe way to change primary providers.
        """
        org_id = uuid4()
        patient_id = uuid4()
        provider1_id = uuid4()
        provider2_id = uuid4()

        # Create initial primary
        assignment1 = CareTeamAssignment(
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=provider1_id,
            is_primary_provider=True
        )
        db_session.add(assignment1)
        await db_session.commit()

        # Add secondary provider
        assignment2 = CareTeamAssignment(
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=provider2_id,
            is_primary_provider=False
        )
        db_session.add(assignment2)
        await db_session.commit()

        # Change primary: demote first, promote second (atomic transaction)
        assignment1.is_primary_provider = False
        assignment2.is_primary_provider = True
        await db_session.commit()  # Should succeed

        # Verify only one primary
        result = await db_session.execute(
            select(CareTeamAssignment).where(
                CareTeamAssignment.patient_id == patient_id,
                CareTeamAssignment.is_primary_provider == True
            )
        )
        primaries = result.scalars().all()
        assert len(primaries) == 1
        assert primaries[0].provider_id == provider2_id


@pytest.mark.asyncio
class TestCareTeamService:
    """Test service layer business logic."""

    async def test_assign_primary_provider_demotes_existing(self, db_session):
        """
        Test that assign_primary_provider automatically demotes existing primary.

        This ensures atomicity and prevents constraint violations.
        """
        org_id = uuid4()
        patient_id = uuid4()
        provider1_id = uuid4()
        provider2_id = uuid4()

        # Assign first primary
        await CareTeamService.assign_primary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=provider1_id
        )

        # Verify first is primary
        primary = await CareTeamService.get_primary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id
        )
        assert primary == provider1_id

        # Assign second primary (should demote first)
        await CareTeamService.assign_primary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=provider2_id
        )

        # Verify second is now primary
        primary = await CareTeamService.get_primary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id
        )
        assert primary == provider2_id

        # Verify only one primary exists
        result = await db_session.execute(
            select(CareTeamAssignment).where(
                CareTeamAssignment.organization_id == org_id,
                CareTeamAssignment.patient_id == patient_id,
                CareTeamAssignment.is_primary_provider == True
            )
        )
        primaries = result.scalars().all()
        assert len(primaries) == 1

    async def test_add_secondary_provider_does_not_affect_primary(self, db_session):
        """
        Test that adding secondary providers doesn't change primary status.
        """
        org_id = uuid4()
        patient_id = uuid4()
        primary_provider_id = uuid4()
        secondary_provider_id = uuid4()

        # Set initial primary
        await CareTeamService.assign_primary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=primary_provider_id
        )

        # Add secondary provider
        await CareTeamService.add_secondary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=secondary_provider_id
        )

        # Verify primary is unchanged
        primary = await CareTeamService.get_primary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id
        )
        assert primary == primary_provider_id

        # Verify two total providers (1 primary + 1 secondary)
        result = await db_session.execute(
            select(CareTeamAssignment).where(
                CareTeamAssignment.organization_id == org_id,
                CareTeamAssignment.patient_id == patient_id
            )
        )
        all_providers = result.scalars().all()
        assert len(all_providers) == 2

    async def test_remove_provider_maintains_constraint(self, db_session):
        """
        Test that removing a provider doesn't violate constraints.
        """
        org_id = uuid4()
        patient_id = uuid4()
        provider_id = uuid4()

        # Assign primary
        await CareTeamService.assign_primary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=provider_id
        )

        # Remove provider
        removed = await CareTeamService.remove_from_care_team(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id,
            provider_id=provider_id
        )
        assert removed is True

        # Verify no primary exists now
        primary = await CareTeamService.get_primary_provider(
            db=db_session,
            organization_id=org_id,
            patient_id=patient_id
        )
        assert primary is None


# ==========================================
# PYTEST FIXTURES
# ==========================================
# NOTE: Add these to conftest.py when setting up test infrastructure

"""
@pytest.fixture
async def db_session():
    '''Provide a clean database session for each test.'''
    async with get_test_db_session() as session:
        yield session
        await session.rollback()  # Rollback after each test
"""
