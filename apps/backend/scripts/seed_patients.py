#!/usr/bin/env python3
"""
Seed script to create 50 realistic dummy patients for development/testing.
Ensures HIPAA compliance by using only synthetic data.

Usage:
    cd backend
    uv run python scripts/seed_patients.py
"""

import asyncio
import random
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models import Organization, OrganizationPatient, Patient
from src.models.contacts import ContactMethod

fake = Faker()
Faker.seed(42)  # Reproducible results

# Configuration
NUM_PATIENTS = 50
NUM_ACTIVE = 45
NUM_DISCHARGED = 5

LEGAL_SEXES = ["Male", "Female", "Other", "Prefer not to say"]
CONTACT_TYPES = ["MOBILE", "HOME", "EMAIL"]
CONTACT_LABELS = {
    "MOBILE": ["Personal Cell", "Mobile"],
    "HOME": ["Home Phone", "Landline"],
    "EMAIL": ["Personal Email", "Work Email"],
}


async def get_test_organization(session: AsyncSession) -> Organization:
    """Get or create the test organization."""
    stmt = select(Organization).where(Organization.name == "Test Organization")
    result = await session.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        # Create test org if it doesn't exist
        org = Organization(
            name="Test Organization",
            settings_json={},
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(org)
        await session.flush()
        print("Created Test Organization")

    return org


def generate_patient_data(mrn_counter: int) -> dict:
    """Generate realistic patient data."""
    # Date of birth: 1940-2020
    start_date = date(1940, 1, 1)
    end_date = date(2020, 12, 31)
    dob = fake.date_between(start_date=start_date, end_date=end_date)

    # Legal sex distribution
    legal_sex = random.choices(
        LEGAL_SEXES,
        weights=[48, 48, 3, 1],  # Roughly equal M/F, small Other/Prefer not to say
    )[0]

    # If legal sex suggests gender, use consistent name generation
    if legal_sex == "Male":
        first_name = fake.first_name_male()
    elif legal_sex == "Female":
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name()

    return {
        "first_name": first_name,
        "last_name": fake.last_name(),
        "dob": dob,
        "legal_sex": legal_sex,
        "medical_record_number": f"MRN-{mrn_counter:06d}",
    }


def generate_contact_methods(patient_id) -> list[ContactMethod]:
    """Generate 1-3 contact methods per patient."""
    now = datetime.now(UTC)
    num_contacts = random.randint(1, 3)
    contacts = []

    # Always include at least one phone as primary
    phone_type = random.choice(["MOBILE", "HOME"])
    contacts.append(
        ContactMethod(
            id=uuid4(),
            patient_id=patient_id,
            type=phone_type,
            value=fake.phone_number(),
            is_primary=True,
            is_safe_for_voicemail=random.choice([True, False]),  # 50/50 split
            label=random.choice(CONTACT_LABELS[phone_type]),
            created_at=now,
            updated_at=now,
        )
    )

    # Add additional contacts
    available_types = ["MOBILE", "HOME", "EMAIL"]
    if phone_type in available_types:
        available_types.remove(phone_type)

    for _ in range(num_contacts - 1):
        if not available_types:
            break
        contact_type = random.choice(available_types)
        available_types.remove(contact_type)

        if contact_type == "EMAIL":
            value = fake.email()
            is_safe = True  # Email is always safe
        else:
            value = fake.phone_number()
            is_safe = random.choice([True, False])

        contacts.append(
            ContactMethod(
                id=uuid4(),
                patient_id=patient_id,
                type=contact_type,
                value=value,
                is_primary=False,
                is_safe_for_voicemail=is_safe,
                label=random.choice(CONTACT_LABELS[contact_type]),
                created_at=now,
                updated_at=now,
            )
        )

    return contacts


async def seed_patients():
    """Main seeding function."""
    print(f"Seeding {NUM_PATIENTS} patients...")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get test organization
        org = await get_test_organization(session)

        # Check if patients already exist
        existing_stmt = select(OrganizationPatient).where(OrganizationPatient.organization_id == org.id)
        existing_result = await session.execute(existing_stmt)
        existing_count = len(existing_result.scalars().all())

        if existing_count >= NUM_PATIENTS:
            print(f"Already have {existing_count} patients. Skipping seed.")
            return

        now = datetime.now(UTC)
        start_mrn = existing_count + 1
        created_count = 0

        for i in range(NUM_PATIENTS - existing_count):
            mrn_counter = start_mrn + i
            patient_data = generate_patient_data(mrn_counter)

            # Create patient
            patient = Patient(
                id=uuid4(),
                first_name=patient_data["first_name"],
                last_name=patient_data["last_name"],
                dob=patient_data["dob"],
                legal_sex=patient_data["legal_sex"],
                medical_record_number=patient_data["medical_record_number"],
                subscription_status="INCOMPLETE",
                created_at=now,
                updated_at=now,
            )
            session.add(patient)
            await session.flush()

            # Determine status
            is_discharged = created_count >= NUM_ACTIVE
            status = "DISCHARGED" if is_discharged else "ACTIVE"
            enrolled_date = now - timedelta(days=random.randint(1, 365))

            # Create enrollment
            enrollment = OrganizationPatient(
                organization_id=org.id,
                patient_id=patient.id,
                status=status,
                enrolled_at=enrolled_date,
                discharged_at=now if is_discharged else None,
            )
            session.add(enrollment)

            # Create contact methods
            contacts = generate_contact_methods(patient.id)
            for contact in contacts:
                session.add(contact)

            created_count += 1
            if created_count % 10 == 0:
                print(f"  Created {created_count}/{NUM_PATIENTS - existing_count} patients...")

        await session.commit()
        print(f"✓ Created {created_count} patients with contact methods")
        print(f"  - Active: {NUM_ACTIVE}")
        print(f"  - Discharged: {NUM_DISCHARGED}")


if __name__ == "__main__":
    asyncio.run(seed_patients())
