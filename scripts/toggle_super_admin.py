import asyncio
import sys
import os
import argparse

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from src.database import AsyncSessionLocal
from src.models import User
from sqlalchemy import select

async def toggle_super_admin(email: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"User {email} not found.")
            return

        user.is_super_admin = not user.is_super_admin
        await session.commit()
        print(f"User {email} is now super_admin={user.is_super_admin}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Toggle super admin status for a user.")
    parser.add_argument("email", help="Email of the user")
    args = parser.parse_args()

    asyncio.run(toggle_super_admin(args.email))
