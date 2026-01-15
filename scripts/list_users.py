import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../apps/backend"))

from src.database import AsyncSessionLocal
from src.models import User
from sqlalchemy import select


async def list_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).order_by(User.email))
        users = result.scalars().all()

        print(f"{'ID':<36} | {'Email':<30} | {'Super Admin':<11}")
        print("-" * 85)
        for user in users:
            print(
                f"{str(user.id):<36} | {user.email:<30} | {str(user.is_super_admin):<11}"
            )


if __name__ == "__main__":
    asyncio.run(list_users())
