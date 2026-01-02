import sys
import os
import asyncio
from datetime import date
from sqlalchemy import delete

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.database import AsyncSessionLocal
from src.models.users import User
from src.models.profiles import Staff, Patient
from src.models.organizations import Organization, OrganizationMember, OrganizationPatient
from src.config import settings

def get_password_hash(password: str) -> str:
    # Dummy hash for legacy password fields.
    # Authentication should use mock flow or Firebase.
    return "dummy_hash"

async def seed():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    async with AsyncSessionLocal() as session:
        print("Wiping data...")
        # Delete in order of dependencies (Child -> Parent)
        await session.execute(delete(OrganizationPatient))
        await session.execute(delete(OrganizationMember))
        await session.execute(delete(Staff))
        await session.execute(delete(Patient))
        await session.execute(delete(Organization))
        await session.execute(delete(User))
        await session.commit()
        print("Data wiped.")

        print("Seeding data...")
        # 1. Create Organization
        org = Organization(
            name="Lockdev Clinic",
            tax_id="12-3456789",
            subscription_status="ACTIVE",
            is_active=True
        )
        session.add(org)
        await session.flush()

        # 2. Create E2E User
        e2e_user = User(
            email="e2e@example.com",
            password_hash=get_password_hash("password"),
            display_name="E2E User",
            is_super_admin=True,
            requires_consent=False,
            transactional_consent=True
        )
        session.add(e2e_user)
        
        # 3. Create Staff User
        staff_user = User(
            email="staff@example.com",
            password_hash=get_password_hash("password"),
            display_name="Staff User",
            is_super_admin=False,
            requires_consent=False,
            transactional_consent=True
        )
        session.add(staff_user)
        await session.flush()

        staff_profile = Staff(
            user_id=staff_user.id,
            job_title="NURSE",
            employee_id="ST-001"
        )
        session.add(staff_profile)

        # Add Staff to Org
        staff_member = OrganizationMember(
            user_id=staff_user.id,
            organization_id=org.id,
            role="STAFF"
        )
        session.add(staff_member)

        # 4. Create Patient User
        patient_user = User(
            email="patient@example.com",
            password_hash=get_password_hash("password"),
            display_name="Patient User",
            requires_consent=False,
            transactional_consent=True
        )
        session.add(patient_user)
        await session.flush()

        patient_profile = Patient(
            user_id=patient_user.id,
            first_name="Test",
            last_name="Patient",
            dob=date(1990, 1, 1),
            subscription_status="ACTIVE",
            medical_record_number="MRN-001",
            legal_sex="M"
        )
        session.add(patient_profile)
        await session.flush() # get patient_profile.id

        # Add Patient to Org
        org_patient = OrganizationPatient(
            organization_id=org.id,
            patient_id=patient_profile.id,
            status="ACTIVE"
        )
        session.add(org_patient)

        await session.commit()
        print("Database seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed())