import asyncio
import os
import random
import sys

from faker import Faker

# Add the backend directory to sys.path to allow importing app
sys.path.append(os.getcwd())

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.contact import ContactMethod
from app.models.organization import Organization
from app.models.profile import Patient

fake = Faker()


async def seed_patients(num_patients=50):
    async with AsyncSessionLocal() as db:
        # Get first organization
        stmt = select(Organization).limit(1)
        result = await db.execute(stmt)
        org = result.scalar_one_or_none()

        if not org:
            # Create a default org if none exists
            org = Organization(
                id="01KF2MCB6VZ6Z6Z6Z6Z6Z6Z6O1", name="Test Hospital", slug="test-hosp"
            )
            db.add(org)
            await db.flush()

        for _i in range(num_patients):
            patient = Patient(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                mrn=f"MRN-{random.randint(100000, 999999)}",
                dob=fake.date_of_birth(minimum_age=0, maximum_age=100),
                gender=random.choice(["M", "F", "Other"]),
                preferred_language=random.choice(["en", "es", "fr"]),
                organization_id=org.id,
            )
            db.add(patient)
            await db.flush()  # Get patient ID

            # Add 1-2 contact methods
            for j in range(random.randint(1, 2)):
                contact = ContactMethod(
                    patient_id=patient.id,
                    type=random.choice(["PHONE", "EMAIL"]),
                    value=fake.phone_number() if j == 0 else fake.email(),
                    is_primary=(j == 0),
                    is_safe_for_voicemail=random.choice([True, False]),
                    label=random.choice(["Home", "Work", "Mobile"]),
                )
                db.add(contact)

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed_patients())
