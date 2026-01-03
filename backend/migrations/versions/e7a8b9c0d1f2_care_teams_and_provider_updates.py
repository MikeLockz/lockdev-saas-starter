"""Add care team assignments and provider/staff updates

Revision ID: e7a8b9c0d1f2
Revises: d4e5f6a7b8c9
Create Date: 2026-01-02 20:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e7a8b9c0d1f2'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =====================================================
    # 1. UPDATE PROVIDERS TABLE
    # =====================================================
    
    # Add new columns to providers
    op.add_column('providers', sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('providers', sa.Column('license_number', sa.String(50), nullable=True))
    op.add_column('providers', sa.Column('license_state', sa.String(2), nullable=True))
    op.add_column('providers', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    
    # Remove unique constraint on user_id if exists (now can have multiple provider profiles per org)
    op.drop_constraint('providers_user_id_key', 'providers', type_='unique')
    
    # Remove global unique constraint on npi_number (will be unique per org via index)
    op.drop_constraint('providers_npi_number_key', 'providers', type_='unique')
    
    # Add foreign key for organization_id
    op.create_foreign_key(
        'fk_providers_organization',
        'providers', 'organizations',
        ['organization_id'], ['id']
    )
    
    # Add unique constraint: NPI must be unique within an organization
    op.create_index(
        'ix_providers_org_npi',
        'providers',
        ['organization_id', 'npi_number'],
        unique=True,
        postgresql_where=sa.text('npi_number IS NOT NULL')
    )
    
    # =====================================================
    # 2. UPDATE STAFF TABLE
    # =====================================================
    
    # Add new columns to staff
    op.add_column('staff', sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('staff', sa.Column('department', sa.String(100), nullable=True))
    op.add_column('staff', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    
    # Remove unique constraint on user_id if exists
    op.drop_constraint('staff_user_id_key', 'staff', type_='unique')
    
    # Add foreign key for organization_id
    op.create_foreign_key(
        'fk_staff_organization',
        'staff', 'organizations',
        ['organization_id'], ['id']
    )
    
    # =====================================================
    # 3. CREATE CARE_TEAM_ASSIGNMENTS TABLE
    # =====================================================
    
    op.create_table(
        'care_team_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='SPECIALIST'),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('removed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name='fk_care_team_organization'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name='fk_care_team_patient'),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], name='fk_care_team_provider'),
        sa.UniqueConstraint('patient_id', 'provider_id', name='uq_care_team_patient_provider'),
        comment='Care team assignments linking providers to patients'
    )
    
    # Index for efficient lookups
    op.create_index(
        'ix_care_team_org_patient',
        'care_team_assignments',
        ['organization_id', 'patient_id']
    )
    
    op.create_index(
        'ix_care_team_active',
        'care_team_assignments',
        ['patient_id'],
        postgresql_where=sa.text('removed_at IS NULL')
    )


def downgrade() -> None:
    # Drop care_team_assignments table
    op.drop_index('ix_care_team_active', table_name='care_team_assignments')
    op.drop_index('ix_care_team_org_patient', table_name='care_team_assignments')
    op.drop_table('care_team_assignments')
    
    # Revert staff changes
    op.drop_constraint('fk_staff_organization', 'staff', type_='foreignkey')
    op.drop_column('staff', 'is_active')
    op.drop_column('staff', 'department')
    op.drop_column('staff', 'organization_id')
    op.create_unique_constraint('staff_user_id_key', 'staff', ['user_id'])
    
    # Revert provider changes
    op.drop_index('ix_providers_org_npi', table_name='providers')
    op.drop_constraint('fk_providers_organization', 'providers', type_='foreignkey')
    op.drop_column('providers', 'is_active')
    op.drop_column('providers', 'license_state')
    op.drop_column('providers', 'license_number')
    op.drop_column('providers', 'organization_id')
    op.create_unique_constraint('providers_npi_number_key', 'providers', ['npi_number'])
    op.create_unique_constraint('providers_user_id_key', 'providers', ['user_id'])
