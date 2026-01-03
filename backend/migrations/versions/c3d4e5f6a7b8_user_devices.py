"""user_devices

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-01-02 12:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_devices table for FCM push notification tokens."""
    op.create_table(
        'user_devices',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fcm_token', sa.String(512), nullable=False),
        sa.Column('device_name', sa.String(255), nullable=True),
        sa.Column('platform', sa.String(20), nullable=True),  # 'ios', 'android', 'web'
        sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Unique constraint for user + token combination
    op.create_unique_constraint(
        'uq_user_devices_user_token',
        'user_devices',
        ['user_id', 'fcm_token']
    )
    
    # Index for querying devices by user
    op.create_index('idx_user_devices_user_id', 'user_devices', ['user_id'])


def downgrade() -> None:
    """Drop user_devices table."""
    op.drop_index('idx_user_devices_user_id')
    op.drop_constraint('uq_user_devices_user_token', 'user_devices')
    op.drop_table('user_devices')
