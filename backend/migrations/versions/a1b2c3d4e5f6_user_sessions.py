"""user_sessions

Revision ID: a1b2c3d4e5f6
Revises: f47bf61a922e
Create Date: 2026-01-02 12:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f47bf61a922e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_sessions table for session tracking."""
    op.create_table(
        'user_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_info', JSONB, nullable=True, server_default='{}'),
        sa.Column('firebase_uid', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),  # IPv6 max length
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('is_revoked', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for common queries
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_user_sessions_active', 'user_sessions', ['user_id', 'is_revoked'])
    op.create_index('idx_user_sessions_firebase_uid', 'user_sessions', ['firebase_uid'])
    
    # Add audit trigger for HIPAA compliance
    op.execute("""
    CREATE TRIGGER audit_trigger_user_sessions
    AFTER INSERT OR UPDATE OR DELETE ON user_sessions
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
    """)


def downgrade() -> None:
    """Drop user_sessions table."""
    op.execute("DROP TRIGGER IF EXISTS audit_trigger_user_sessions ON user_sessions")
    op.drop_index('idx_user_sessions_firebase_uid')
    op.drop_index('idx_user_sessions_active')
    op.drop_index('idx_user_sessions_user_id')
    op.drop_table('user_sessions')
