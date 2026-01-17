from typing import Any

import pytest
import sqlalchemy as sa
from postgresql_audit import versioning_manager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column

from app.core.audit_sql import (
    SQL_AUDIT_TABLE_MAIN,
    SQL_AUDIT_TABLE_WRAPPER,
    SQL_CREATE_ACTIVITY,
    SQL_CREATE_OPERATOR_MINUS,
    SQL_GET_SETTING,
    SQL_JSONB_CHANGE_KEY_NAME,
    SQL_JSONB_SUBTRACT,
)
from app.core.config import settings
from app.core.models_base import Base


# Define a test model
class Article(Base):
    __tablename__ = "article"
    __versioned__: dict[str, Any] = {}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


@pytest.mark.skip(reason="Depends on versioning_manager which is mocked in tests")
@pytest.mark.asyncio
async def test_audit_log():
    # Create a fresh engine for this test
    test_engine = create_async_engine(settings.sqlalchemy_database_uri)
    test_async_session_local = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    # Remove the problematic listeners if present
    activity_table = versioning_manager.activity_cls.__table__
    if sa.event.contains(
        activity_table, "after_create", versioning_manager.create_audit_table
    ):
        sa.event.remove(
            activity_table, "after_create", versioning_manager.create_audit_table
        )
    if sa.event.contains(
        activity_table, "after_create", versioning_manager.create_operators
    ):
        sa.event.remove(
            activity_table, "after_create", versioning_manager.create_operators
        )

    async with test_engine.begin() as conn:
        # We need extensions
        await conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS btree_gist"))

        await conn.run_sync(Base.metadata.create_all)

        # Manually execute audit setup
        await conn.execute(sa.text(SQL_JSONB_CHANGE_KEY_NAME))
        await conn.execute(sa.text(SQL_GET_SETTING))

        # Operators
        await conn.execute(
            sa.text("DROP FUNCTION IF EXISTS jsonb_subtract(jsonb,jsonb) CASCADE")
        )
        await conn.execute(sa.text(SQL_JSONB_SUBTRACT))
        await conn.execute(sa.text("DROP OPERATOR IF EXISTS - (jsonb, jsonb)"))
        await conn.execute(sa.text(SQL_CREATE_OPERATOR_MINUS))

        await conn.execute(sa.text(SQL_CREATE_ACTIVITY))
        await conn.execute(sa.text(SQL_AUDIT_TABLE_MAIN))
        await conn.execute(sa.text(SQL_AUDIT_TABLE_WRAPPER))

        # Trigger on article
        await conn.execute(sa.text("SELECT audit_table('article')"))

    async with test_async_session_local() as session:
        article = Article(name="Test Article")
        session.add(article)
        await session.commit()

        # Verify activity
        result = await session.execute(
            sa.text("SELECT * FROM activity WHERE table_name = 'article'")
        )
        activities = result.fetchall()
        assert len(activities) == 1
        assert activities[0].table_name == "article"
        assert activities[0].verb == "insert"
        # Check data
        print(activities[0].changed_data)
        assert activities[0].changed_data.get("name") == "Test Article"

    await test_engine.dispose()
