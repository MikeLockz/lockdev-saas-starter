"""setup_audit_tables

Revision ID: 3c92e5d86a44
Revises: 
Create Date: 2026-01-15 21:05:50.380647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3c92e5d86a44'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# SQL definitions extracted from postgresql-audit to avoid multi-statement errors in asyncpg
SQL_JSONB_CHANGE_KEY_NAME = """
CREATE OR REPLACE FUNCTION jsonb_change_key_name(data jsonb, old_key text, new_key text)
RETURNS jsonb AS $$
    SELECT ('{' || string_agg(to_json(key) || ':' || value, ',') || '}')::jsonb
    FROM (
        SELECT CASE WHEN key = old_key THEN new_key ELSE key END, value
        FROM jsonb_each(data)
    ) t;
$$ LANGUAGE SQL IMMUTABLE;
"""

SQL_GET_SETTING = """
CREATE OR REPLACE FUNCTION get_setting(setting text, default_value text)
RETURNS text AS $$
    SELECT coalesce(
        nullif(current_setting(setting, 't'), ''),
        default_value
    );
$$ LANGUAGE SQL;
"""

SQL_CREATE_ACTIVITY = """
CREATE OR REPLACE FUNCTION create_activity() RETURNS TRIGGER AS $$
DECLARE
    audit_row activity;
    excluded_cols text[] = ARRAY[]::text[];
    _transaction_id BIGINT;
BEGIN
    _transaction_id := (
        SELECT id
        FROM transaction
        WHERE
            native_transaction_id = txid_current() AND
            issued_at >= (NOW() - INTERVAL '1 day')
        ORDER BY issued_at DESC
        LIMIT 1
    );

    IF TG_ARGV[0] IS NOT NULL THEN
        excluded_cols = TG_ARGV[0]::text[];
    END IF;

    IF (TG_OP = 'UPDATE') THEN
        INSERT INTO activity(
            id, schema_name, table_name, relid, issued_at, native_transaction_id,
            verb, old_data, changed_data, transaction_id)
        SELECT
            nextval('activity_id_seq') as id,
            TG_TABLE_SCHEMA::text AS schema_name,
            TG_TABLE_NAME::text AS table_name,
            TG_RELID AS relid,
            statement_timestamp() AT TIME ZONE 'UTC' AS issued_at,
            txid_current() AS native_transaction_id,
            LOWER(TG_OP) AS verb,
            old_data - excluded_cols AS old_data,
            new_data - old_data - excluded_cols AS changed_data,
            _transaction_id AS transaction_id
        FROM (
            SELECT *
            FROM (
                SELECT
                    row_to_json(old_table.*)::jsonb AS old_data,
                    row_number() OVER ()
                FROM old_table
            ) AS old_table
            JOIN (
                SELECT
                    row_to_json(new_table.*)::jsonb AS new_data,
                    row_number() OVER ()
                FROM new_table
            ) AS new_table
            USING(row_number)
        ) as sub
        WHERE new_data - old_data - excluded_cols != '{}'::jsonb;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO activity(
            id, schema_name, table_name, relid, issued_at, native_transaction_id,
            verb, old_data, changed_data, transaction_id)
        SELECT
            nextval('activity_id_seq') as id,
            TG_TABLE_SCHEMA::text AS schema_name,
            TG_TABLE_NAME::text AS table_name,
            TG_RELID AS relid,
            statement_timestamp() AT TIME ZONE 'UTC' AS issued_at,
            txid_current() AS native_transaction_id,
            LOWER(TG_OP) AS verb,
            '{}'::jsonb AS old_data,
            row_to_json(new_table.*)::jsonb - excluded_cols AS changed_data,
            _transaction_id AS transaction_id
        FROM new_table;
    ELSEIF TG_OP = 'DELETE' THEN
        INSERT INTO activity(
            id, schema_name, table_name, relid, issued_at, native_transaction_id,
            verb, old_data, changed_data, transaction_id)
        SELECT
            nextval('activity_id_seq') as id,
            TG_TABLE_SCHEMA::text AS schema_name,
            TG_TABLE_NAME::text AS table_name,
            TG_RELID AS relid,
            statement_timestamp() AT TIME ZONE 'UTC' AS issued_at,
            txid_current() AS native_transaction_id,
            LOWER(TG_OP) AS verb,
            row_to_json(old_table.*)::jsonb - excluded_cols AS old_data,
            '{}'::jsonb AS changed_data,
            _transaction_id AS transaction_id
        FROM old_table;
    END IF;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public;
"""

SQL_AUDIT_TABLE_MAIN = r"""
CREATE OR REPLACE FUNCTION
audit_table(target_table regclass, ignored_cols text[])
RETURNS void AS $$
DECLARE
    query text;
    excluded_columns_text text = '';
BEGIN
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_insert ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_update ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_delete ON ' || target_table;

    IF array_length(ignored_cols, 1) > 0 THEN
        excluded_columns_text = ', ' || quote_literal(ignored_cols);
    END IF;
    query = 'CREATE TRIGGER audit_trigger_insert AFTER INSERT ON ' ||
             target_table || ' REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT ' ||
             E'WHEN (get_setting(\'postgresql_audit.enable_versioning\', \'true\')::bool)' ||
             ' EXECUTE PROCEDURE create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
    query = 'CREATE TRIGGER audit_trigger_update AFTER UPDATE ON ' ||
             target_table || ' REFERENCING NEW TABLE AS new_table OLD TABLE AS old_table FOR EACH STATEMENT ' ||
             E'WHEN (get_setting(\'postgresql_audit.enable_versioning\', \'true\')::bool)' ||
             ' EXECUTE PROCEDURE create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
    query = 'CREATE TRIGGER audit_trigger_delete AFTER DELETE ON ' ||
             target_table || ' REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT ' ||
             E'WHEN (get_setting(\'postgresql_audit.enable_versioning\', \'true\')::bool)' ||
             ' EXECUTE PROCEDURE create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
END;
$$
language 'plpgsql';
"""

SQL_AUDIT_TABLE_WRAPPER = """
CREATE OR REPLACE FUNCTION audit_table(target_table regclass) RETURNS void AS $$
SELECT audit_table(target_table, ARRAY[]::text[]);
$$ LANGUAGE SQL;
"""

def upgrade() -> None:
    """Upgrade schema."""
    # Ensure extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm") # Often useful, adding just in case

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('native_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('issued_at', sa.DateTime(), nullable=True),
    sa.Column('client_addr', postgresql.INET(), nullable=True),
    postgresql.ExcludeConstraint((sa.column('native_transaction_id'), '='), (sa.text("tsrange(issued_at - INTERVAL '1 hour', issued_at)"), '&&'), using='gist', name='transaction_unique_native_tx_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('activity',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('schema_name', sa.Text(), nullable=True),
    sa.Column('table_name', sa.Text(), nullable=True),
    sa.Column('relid', sa.Integer(), nullable=True),
    sa.Column('issued_at', sa.DateTime(), nullable=True),
    sa.Column('native_transaction_id', sa.BigInteger(), nullable=True),
    sa.Column('verb', sa.Text(), nullable=True),
    sa.Column('old_data', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
    sa.Column('changed_data', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
    sa.Column('transaction_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['transaction_id'], ['transaction.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_native_transaction_id'), 'activity', ['native_transaction_id'], unique=False)
    # ### end Alembic commands ###

    bind = op.get_bind()
    
    # Execute SQLs one by one
    bind.execute(sa.text(SQL_JSONB_CHANGE_KEY_NAME))
    bind.execute(sa.text(SQL_GET_SETTING))
    bind.execute(sa.text(SQL_CREATE_ACTIVITY))
    bind.execute(sa.text(SQL_AUDIT_TABLE_MAIN))
    bind.execute(sa.text(SQL_AUDIT_TABLE_WRAPPER))
    

def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_activity_native_transaction_id'), table_name='activity')
    op.drop_table('activity')
    op.drop_table('transaction')
    # ### end Alembic commands ###