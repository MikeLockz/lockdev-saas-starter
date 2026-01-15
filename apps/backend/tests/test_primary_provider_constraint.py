"""
Tests for the PRIMARY provider constraint enforcement.

This test suite verifies that the unique partial index 'uq_care_team_primary'
correctly enforces the business rule: only one PRIMARY provider per patient.

Migration: n8o9p0q1r2s3_add_primary_provider_constraint
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from src.models.care_teams import CareTeamAssignment


class TestPrimaryProviderConstraint:
    """Test cases for PRIMARY provider uniqueness constraint."""

    async def test_one_primary_provider_per_patient(
        self, db_session, test_organization, test_patient, test_provider, test_provider_2
    ):
        """Test that only one PRIMARY provider can be assigned per patient."""
        # First PRIMARY assignment should succeed
        assignment1 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider.id,
            role="PRIMARY",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment1)
        await db_session.commit()

        # Verify first assignment was created
        await db_session.refresh(assignment1)
        assert assignment1.role == "PRIMARY"

        # Second PRIMARY assignment should fail with IntegrityError
        assignment2 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider_2.id,
            role="PRIMARY",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        # Verify the error is due to the unique constraint
        assert "uq_care_team_primary" in str(exc_info.value)

    async def test_multiple_specialist_providers_allowed(
        self, db_session, test_organization, test_patient, test_provider, test_provider_2
    ):
        """Test that multiple SPECIALIST providers can be assigned per patient."""
        # First SPECIALIST assignment
        assignment1 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider.id,
            role="SPECIALIST",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment1)
        await db_session.commit()

        # Second SPECIALIST assignment should succeed
        assignment2 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider_2.id,
            role="SPECIALIST",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment2)
        await db_session.commit()

        # Both assignments should exist
        await db_session.refresh(assignment1)
        await db_session.refresh(assignment2)
        assert assignment1.role == "SPECIALIST"
        assert assignment2.role == "SPECIALIST"

    async def test_soft_deleted_primary_allows_new_primary(
        self, db_session, test_organization, test_patient, test_provider, test_provider_2
    ):
        """Test that soft-deleting PRIMARY allows assigning a new PRIMARY provider."""
        # Create first PRIMARY assignment
        assignment1 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider.id,
            role="PRIMARY",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment1)
        await db_session.commit()

        # Soft-delete the first PRIMARY assignment
        assignment1.removed_at = datetime.now(UTC)
        await db_session.commit()

        # Now assigning a new PRIMARY should succeed
        assignment2 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider_2.id,
            role="PRIMARY",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment2)
        await db_session.commit()

        # Verify new PRIMARY assignment exists
        await db_session.refresh(assignment2)
        assert assignment2.role == "PRIMARY"
        assert assignment2.removed_at is None

    async def test_multiple_consultant_providers_allowed(
        self, db_session, test_organization, test_patient, test_provider, test_provider_2
    ):
        """Test that multiple CONSULTANT providers can be assigned per patient."""
        # First CONSULTANT assignment
        assignment1 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider.id,
            role="CONSULTANT",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment1)
        await db_session.commit()

        # Second CONSULTANT assignment should succeed
        assignment2 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider_2.id,
            role="CONSULTANT",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment2)
        await db_session.commit()

        # Both assignments should exist
        await db_session.refresh(assignment1)
        await db_session.refresh(assignment2)
        assert assignment1.role == "CONSULTANT"
        assert assignment2.role == "CONSULTANT"

    async def test_primary_reassignment_workflow(
        self, db_session, test_organization, test_patient, test_provider, test_provider_2
    ):
        """Test the workflow of reassigning PRIMARY from one provider to another."""
        # Assign first PRIMARY provider
        assignment1 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider.id,
            role="PRIMARY",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment1)
        await db_session.commit()

        # To reassign PRIMARY, we must first remove or change the existing PRIMARY
        # Option 1: Soft delete
        assignment1.removed_at = datetime.now(UTC)
        await db_session.commit()

        # Now assign new PRIMARY provider
        assignment2 = CareTeamAssignment(
            id=uuid4(),
            organization_id=test_organization.id,
            patient_id=test_patient.id,
            provider_id=test_provider_2.id,
            role="PRIMARY",
            assigned_at=datetime.now(UTC),
        )
        db_session.add(assignment2)
        await db_session.commit()

        # Verify the reassignment
        await db_session.refresh(assignment2)
        assert assignment2.role == "PRIMARY"
        assert assignment2.removed_at is None
