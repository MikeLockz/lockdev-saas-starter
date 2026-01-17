import asyncio
import os
import sys

# Add the backend directory to sys.path to allow importing app
sys.path.append(os.getcwd())

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.user import User


async def seed():
    async with AsyncSessionLocal() as db:
        # Check if test user exists
        stmt = select(User).where(User.email == "test-e2e@example.com")
        res = await db.execute(stmt)
        if not res.scalar_one_or_none():
            user = User(email="test-e2e@example.com", is_active=True, is_superuser=True)
            db.add(user)
            await db.commit()
        else:
            pass


if __name__ == "__main__":
    asyncio.run(seed())
