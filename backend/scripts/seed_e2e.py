import sys
import os
import asyncio
import secrets
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import delete

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.database import AsyncSessionLocal
from src.models import (
    User, Staff, Patient, Provider, Proxy,
    Organization, OrganizationMember, OrganizationPatient,
    CareTeamAssignment, PatientProxyAssignment,
    Call, Task, Appointment, Document,
    Notification, MessageThread, MessageParticipant, Message,
    SupportTicket, SupportMessage,
    AuditLog, UserSession, UserDevice,
    Invitation, ContactMethod, ConsentDocument, UserConsent
)
from src.config import settings

def get_password_hash(password: str) -> str:
    # Dummy hash for legacy password fields.
    # Authentication should use mock flow or Firebase.
    return "dummy_hash"

def now() -> datetime:
    return datetime.now(timezone.utc)

async def seed():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    async with AsyncSessionLocal() as session:
        print("Wiping data...")
        # Delete in order of dependencies (Child -> Parent)
        
        # 1. Activities and Logs
        await session.execute(delete(AuditLog))
        await session.execute(delete(UserSession))
        await session.execute(delete(UserDevice))
        
        # 2. Communications and Operations
        await session.execute(delete(Message))
        await session.execute(delete(MessageParticipant))
        await session.execute(delete(MessageThread))
        await session.execute(delete(Notification))
        await session.execute(delete(SupportMessage))
        await session.execute(delete(SupportTicket))
        await session.execute(delete(Call))
        await session.execute(delete(Task))
        
        # 3. Clinical / Workflow
        await session.execute(delete(Appointment))
        await session.execute(delete(Document))
        await session.execute(delete(CareTeamAssignment))
        await session.execute(delete(PatientProxyAssignment))
        
        # 4. Profiles and Memberships
        await session.execute(delete(OrganizationPatient))
        await session.execute(delete(OrganizationMember))
        await session.execute(delete(Staff))
        await session.execute(delete(Patient))
        await session.execute(delete(Provider))
        await session.execute(delete(Proxy))
        
        # 5. Core
        await session.execute(delete(Invitation))
        await session.execute(delete(ContactMethod))
        await session.execute(delete(UserConsent))
        await session.execute(delete(ConsentDocument))
        await session.execute(delete(Organization))
        await session.execute(delete(User))
        
        await session.commit()
        print("Data wiped.")

        print("Seeding core entities...")
        # ============================================================
        # 1. ORGANIZATION
        # ============================================================
        org = Organization(
            name="Lockdev Clinic",
            tax_id="12-3456789",
            subscription_status="ACTIVE",
            is_active=True
        )
        session.add(org)
        await session.flush()
        print(f"  ✓ Organization: {org.name}")

        # ============================================================
        # 2. USERS
        # ============================================================
        # E2E / Super Admin User
        e2e_user = User(
            email="e2e@example.com",
            password_hash=get_password_hash("password"),
            display_name="E2E User",
            is_super_admin=True,
            requires_consent=False,
            transactional_consent=True
        )
        session.add(e2e_user)
        
        # Staff User
        staff_user = User(
            email="staff@example.com",
            password_hash=get_password_hash("password"),
            display_name="Staff User",
            is_super_admin=False,
            requires_consent=False,
            transactional_consent=True
        )
        session.add(staff_user)
        
        # Provider User 1
        provider_user = User(
            email="provider@example.com",
            password_hash=get_password_hash("password"),
            display_name="Dr. Jane Smith",
            is_super_admin=False,
            requires_consent=False,
            transactional_consent=True
        )
        session.add(provider_user)
        
        # Provider User 2 (for care team variety)
        provider_user2 = User(
            email="provider2@example.com",
            password_hash=get_password_hash("password"),
            display_name="Dr. Michael Chen",
            is_super_admin=False,
            requires_consent=False,
            transactional_consent=True
        )
        session.add(provider_user2)

        # Patient User
        patient_user = User(
            email="patient@example.com",
            password_hash=get_password_hash("password"),
            display_name="Patient User",
            requires_consent=False,
            transactional_consent=True
        )
        session.add(patient_user)
        
        # Proxy User
        proxy_user = User(
            email="proxy@example.com",
            password_hash=get_password_hash("password"),
            display_name="Proxy User (Parent)",
            requires_consent=False,
            transactional_consent=True
        )
        session.add(proxy_user)
        
        await session.flush()
        print(f"  ✓ Users: 6 created")

        # ============================================================
        # 3. PROFILES
        # ============================================================
        # Staff Profile
        staff_profile = Staff(
            user_id=staff_user.id,
            organization_id=org.id,
            job_title="NURSE",
            employee_id="ST-001"
        )
        session.add(staff_profile)

        # Provider Profile 1
        provider_profile = Provider(
            user_id=provider_user.id,
            organization_id=org.id,
            npi_number="1234567890",
            specialty="Internal Medicine",
            license_number="MD-12345",
            license_state="CA",
            is_active=True
        )
        session.add(provider_profile)
        
        # Provider Profile 2
        provider_profile2 = Provider(
            user_id=provider_user2.id,
            organization_id=org.id,
            npi_number="0987654321",
            specialty="Cardiology",
            license_number="MD-67890",
            license_state="CA",
            is_active=True
        )
        session.add(provider_profile2)
        
        await session.flush()

        # Patient Profile
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
        
        # Second Patient Profile (minor child managed by proxy)
        patient_profile2 = Patient(
            user_id=None,  # Minor child has no user account
            first_name="Emma",
            last_name="Johnson",
            dob=date(2018, 6, 15),
            subscription_status="ACTIVE",
            medical_record_number="MRN-002",
            legal_sex="F"
        )
        session.add(patient_profile2)
        await session.flush()
        
        # Proxy Profile
        proxy_profile = Proxy(
            user_id=proxy_user.id,
            relationship_to_patient="PARENT"
        )
        session.add(proxy_profile)
        await session.flush()
        print(f"  ✓ Profiles: Staff, 2 Providers, 2 Patients, Proxy")

        # ============================================================
        # 4. ORGANIZATION MEMBERSHIPS
        # ============================================================
        # Staff Member
        staff_member = OrganizationMember(
            user_id=staff_user.id,
            organization_id=org.id,
            role="STAFF"
        )
        session.add(staff_member)

        # Provider Members
        provider_member = OrganizationMember(
            user_id=provider_user.id,
            organization_id=org.id,
            role="PROVIDER"
        )
        session.add(provider_member)
        
        provider_member2 = OrganizationMember(
            user_id=provider_user2.id,
            organization_id=org.id,
            role="PROVIDER"
        )
        session.add(provider_member2)
        
        # Patient Member (so patient user can access org data in dashboard)
        patient_member = OrganizationMember(
            user_id=patient_user.id,
            organization_id=org.id,
            role="PATIENT"
        )
        session.add(patient_member)
        
        # Proxy Member (so proxy user can access org data in dashboard)
        proxy_member = OrganizationMember(
            user_id=proxy_user.id,
            organization_id=org.id,
            role="PROXY"
        )
        session.add(proxy_member)

        # Patient in Org
        org_patient = OrganizationPatient(
            organization_id=org.id,
            patient_id=patient_profile.id,
            status="ACTIVE"
        )
        session.add(org_patient)
        
        # Second Patient in Org (minor child)
        org_patient2 = OrganizationPatient(
            organization_id=org.id,
            patient_id=patient_profile2.id,
            status="ACTIVE"
        )
        session.add(org_patient2)
        print(f"  ✓ Organization memberships created")

        # ============================================================
        # 5. PROXY ASSIGNMENT
        # ============================================================
        proxy_assignment = PatientProxyAssignment(
            proxy_id=proxy_profile.id,
            patient_id=patient_profile.id,
            relationship_type="PARENT",
            can_view_profile=True,
            can_view_appointments=True,
            can_schedule_appointments=True,
            can_view_clinical_notes=False,
            can_view_billing=False,
            can_message_providers=True,
            granted_at=now(),
            expires_at=now() + timedelta(days=365)
        )
        session.add(proxy_assignment)
        
        # Second Proxy Assignment (parent managing minor child - full access)
        proxy_assignment2 = PatientProxyAssignment(
            proxy_id=proxy_profile.id,
            patient_id=patient_profile2.id,
            relationship_type="GUARDIAN",
            can_view_profile=True,
            can_view_appointments=True,
            can_schedule_appointments=True,
            can_view_clinical_notes=True,
            can_view_billing=True,
            can_message_providers=True,
            granted_at=now(),
            expires_at=None  # No expiration for guardian of minor
        )
        session.add(proxy_assignment2)
        print(f"  ✓ Proxy assignments created (2 patients)")

        # ============================================================
        # 6. CARE TEAM ASSIGNMENTS
        # ============================================================
        print("Seeding care team assignments...")
        # Primary provider (active)
        care_team_primary = CareTeamAssignment(
            organization_id=org.id,
            patient_id=patient_profile.id,
            provider_id=provider_profile.id,
            role="PRIMARY",
            assigned_at=now() - timedelta(days=90)
        )
        session.add(care_team_primary)
        
        # Specialist (active)
        care_team_specialist = CareTeamAssignment(
            organization_id=org.id,
            patient_id=patient_profile.id,
            provider_id=provider_profile2.id,
            role="SPECIALIST",
            assigned_at=now() - timedelta(days=30)
        )
        session.add(care_team_specialist)
        print(f"  ✓ Care team: 2 assignments (PRIMARY, SPECIALIST)")

        # ============================================================
        # 7. CALLS
        # ============================================================
        print("Seeding calls...")
        calls_data = [
            {"direction": "INBOUND", "status": "QUEUED", "outcome": None, "started_at": None, "ended_at": None},
            {"direction": "INBOUND", "status": "IN_PROGRESS", "outcome": None, "started_at": now() - timedelta(minutes=5), "ended_at": None},
            {"direction": "INBOUND", "status": "COMPLETED", "outcome": "RESOLVED", "started_at": now() - timedelta(hours=2), "ended_at": now() - timedelta(hours=2) + timedelta(minutes=15), "duration_seconds": 900},
            {"direction": "OUTBOUND", "status": "COMPLETED", "outcome": "CALLBACK_SCHEDULED", "started_at": now() - timedelta(hours=4), "ended_at": now() - timedelta(hours=4) + timedelta(minutes=8), "duration_seconds": 480},
            {"direction": "OUTBOUND", "status": "COMPLETED", "outcome": "TRANSFERRED", "started_at": now() - timedelta(hours=6), "ended_at": now() - timedelta(hours=6) + timedelta(minutes=3), "duration_seconds": 180},
            {"direction": "INBOUND", "status": "MISSED", "outcome": "VOICEMAIL", "started_at": now() - timedelta(hours=8), "ended_at": now() - timedelta(hours=8) + timedelta(seconds=30), "duration_seconds": 30},
        ]
        for i, c in enumerate(calls_data):
            call = Call(
                organization_id=org.id,
                patient_id=patient_profile.id if i % 2 == 0 else None,
                agent_id=staff_user.id,
                direction=c["direction"],
                status=c["status"],
                phone_number=f"+1555010{i:04d}",
                started_at=c.get("started_at"),
                ended_at=c.get("ended_at"),
                duration_seconds=c.get("duration_seconds"),
                outcome=c["outcome"],
                notes=f"Test call {i+1}" if c["status"] == "COMPLETED" else None
            )
            session.add(call)
        print(f"  ✓ Calls: 6 created (QUEUED, IN_PROGRESS, COMPLETED×3, MISSED)")

        # ============================================================
        # 8. TASKS
        # ============================================================
        print("Seeding tasks...")
        today = date.today()
        # Tasks assigned to staff
        staff_tasks_data = [
            {"status": "TODO", "priority": "URGENT", "due_date": today - timedelta(days=1), "title": "Urgent: Follow up on lab results"},
            {"status": "TODO", "priority": "HIGH", "due_date": today, "title": "Call patient about prescription refill"},
            {"status": "IN_PROGRESS", "priority": "HIGH", "due_date": today, "title": "Insurance pre-authorization"},
            {"status": "DONE", "priority": "LOW", "due_date": today - timedelta(days=3), "title": "Update patient contact info", "completed_at": now() - timedelta(days=2)},
        ]
        for t in staff_tasks_data:
            task = Task(
                organization_id=org.id,
                patient_id=patient_profile.id,
                assignee_id=staff_user.id,
                created_by_id=provider_user.id,
                title=t["title"],
                description=f"Description for: {t['title']}",
                status=t["status"],
                priority=t["priority"],
                due_date=t["due_date"],
                completed_at=t.get("completed_at")
            )
            session.add(task)
        
        # Tasks assigned to provider (for Provider Dashboard)
        provider_tasks_data = [
            {"status": "TODO", "priority": "URGENT", "due_date": today, "title": "Review CT scan results - Patient Smith"},
            {"status": "TODO", "priority": "HIGH", "due_date": today, "title": "Sign off on discharge summary"},
            {"status": "TODO", "priority": "MEDIUM", "due_date": today + timedelta(days=1), "title": "Complete referral letter for cardiology"},
            {"status": "IN_PROGRESS", "priority": "HIGH", "due_date": today, "title": "Medication reconciliation for Test Patient"},
            {"status": "DONE", "priority": "MEDIUM", "due_date": today - timedelta(days=1), "title": "Review lab results", "completed_at": now() - timedelta(hours=4)},
        ]
        for t in provider_tasks_data:
            task = Task(
                organization_id=org.id,
                patient_id=patient_profile.id,
                assignee_id=provider_user.id,
                created_by_id=staff_user.id,
                title=t["title"],
                description=f"Description for: {t['title']}",
                status=t["status"],
                priority=t["priority"],
                due_date=t["due_date"],
                completed_at=t.get("completed_at")
            )
            session.add(task)
        print(f"  ✓ Tasks: 9 created (4 for staff, 5 for provider)")

        # ============================================================
        # 9. APPOINTMENTS
        # ============================================================
        print("Seeding appointments...")
        # Past and future appointments
        appts_data = [
            {"status": "SCHEDULED", "type": "INITIAL", "offset_days": 7, "hour": 10, "reason": "New patient consultation"},
            {"status": "SCHEDULED", "type": "FOLLOW_UP", "offset_days": 1, "hour": 14, "reason": "Follow up on treatment"},
            {"status": "COMPLETED", "type": "INITIAL", "offset_days": -14, "hour": 10, "reason": "Initial visit", "notes": "Patient in good health. Follow up in 2 weeks."},
            {"status": "CANCELLED", "type": "FOLLOW_UP", "offset_days": -7, "hour": 11, "reason": "Routine checkup", "cancellation_reason": "Patient requested reschedule"},
            {"status": "NO_SHOW", "type": "URGENT", "offset_days": -3, "hour": 9, "reason": "Urgent symptoms"},
        ]
        for a in appts_data:
            appt_time = now().replace(hour=a["hour"], minute=0, second=0, microsecond=0) + timedelta(days=a["offset_days"])
            appt = Appointment(
                organization_id=org.id,
                patient_id=patient_profile.id,
                provider_id=provider_profile.id,
                scheduled_at=appt_time,
                duration_minutes=30,
                status=a["status"],
                appointment_type=a["type"],
                reason=a["reason"],
                notes=a.get("notes"),
                cancelled_at=now() - timedelta(days=1) if a["status"] == "CANCELLED" else None,
                cancelled_by=staff_user.id if a["status"] == "CANCELLED" else None,
                cancellation_reason=a.get("cancellation_reason")
            )
            session.add(appt)
        
        # TODAY's appointments for Provider Dashboard (multiple at specific times)
        today_appts = [
            {"status": "CONFIRMED", "type": "FOLLOW_UP", "hour": 9, "minute": 0, "reason": "Post-op check - healing well", "patient_name": "Sarah Johnson"},
            {"status": "SCHEDULED", "type": "INITIAL", "hour": 10, "minute": 30, "reason": "New patient evaluation", "patient_name": "Mike Thompson"},
            {"status": "CONFIRMED", "type": "FOLLOW_UP", "hour": 11, "minute": 0, "reason": "Blood pressure follow-up", "patient_name": "Emily Davis"},
            {"status": "SCHEDULED", "type": "URGENT", "hour": 14, "minute": 0, "reason": "Acute back pain evaluation", "patient_name": "Robert Wilson"},
            {"status": "CONFIRMED", "type": "FOLLOW_UP", "hour": 15, "minute": 30, "reason": "Diabetes management review", "patient_name": "Test Patient"},
        ]
        for ta in today_appts:
            appt_time = now().replace(hour=ta["hour"], minute=ta["minute"], second=0, microsecond=0)
            appt = Appointment(
                organization_id=org.id,
                patient_id=patient_profile.id,  # Using our seeded patient for simplicity
                provider_id=provider_profile.id,
                scheduled_at=appt_time,
                duration_minutes=30,
                status=ta["status"],
                appointment_type=ta["type"],
                reason=ta["reason"],
                notes=None
            )
            session.add(appt)
        print(f"  ✓ Appointments: 10 created (5 past/future, 5 today for Provider Dashboard)")

        # ============================================================
        # 10. DOCUMENTS
        # ============================================================
        print("Seeding documents...")
        docs_data = [
            {"status": "PENDING", "doc_type": "LAB_RESULT", "file_name": "blood_work_2024.pdf", "file_type": "application/pdf", "size": 102400},
            {"status": "CONFIRMED", "doc_type": "LAB_RESULT", "file_name": "cholesterol_panel.pdf", "file_type": "application/pdf", "size": 85000},
            {"status": "CONFIRMED", "doc_type": "INSURANCE_CARD", "file_name": "insurance_front.jpg", "file_type": "image/jpeg", "size": 256000},
            {"status": "CONFIRMED", "doc_type": "CONSENT_FORM", "file_name": "hipaa_consent_signed.pdf", "file_type": "application/pdf", "size": 45000},
            {"status": "CONFIRMED", "doc_type": "OTHER", "file_name": "patient_notes.txt", "file_type": "text/plain", "size": 2048},
        ]
        for i, d in enumerate(docs_data):
            doc = Document(
                organization_id=org.id,
                patient_id=patient_profile.id,
                uploaded_by_user_id=staff_user.id,
                file_name=d["file_name"],
                file_type=d["file_type"],
                file_size=d["size"],
                s3_key=f"org/{org.id}/patients/{patient_profile.id}/{secrets.token_hex(8)}/{d['file_name']}",
                document_type=d["doc_type"],
                description=f"Test document: {d['doc_type']}",
                status=d["status"],
                uploaded_at=now() - timedelta(days=i) if d["status"] == "CONFIRMED" else None
            )
            session.add(doc)
        print(f"  ✓ Documents: 5 created (PENDING×1, CONFIRMED×4)")

        # ============================================================
        # 11. NOTIFICATIONS
        # ============================================================
        print("Seeding notifications...")
        notifications_data = [
            {"user": patient_user, "type": "APPOINTMENT", "title": "Upcoming Appointment", "body": "You have an appointment tomorrow at 10:00 AM", "is_read": False},
            {"user": patient_user, "type": "APPOINTMENT", "title": "Appointment Confirmed", "body": "Your appointment has been confirmed", "is_read": False},
            {"user": patient_user, "type": "MESSAGE", "title": "New Message", "body": "You have a new message from Dr. Smith", "is_read": False},
            {"user": patient_user, "type": "MESSAGE", "title": "Message Reply", "body": "Dr. Smith replied to your message", "is_read": True, "read_at": now() - timedelta(hours=2)},
            {"user": staff_user, "type": "SYSTEM", "title": "System Update", "body": "New features are available", "is_read": False},
            {"user": e2e_user, "type": "BILLING", "title": "Invoice Ready", "body": "Your monthly invoice is ready for review", "is_read": True, "read_at": now() - timedelta(days=1)},
            # Provider notifications
            {"user": provider_user, "type": "APPOINTMENT", "title": "New Appointment Request", "body": "Patient Test Patient has requested an appointment", "is_read": False},
            {"user": provider_user, "type": "MESSAGE", "title": "New Patient Message", "body": "You have a new message from Test Patient", "is_read": False},
            {"user": provider_user, "type": "SYSTEM", "title": "Schedule Update", "body": "Tomorrow's schedule has been updated", "is_read": False},
            {"user": provider_user, "type": "APPOINTMENT", "title": "Appointment Reminder", "body": "You have 3 appointments today", "is_read": True, "read_at": now() - timedelta(hours=4)},
            {"user": provider_user2, "type": "MESSAGE", "title": "Consultation Request", "body": "Dr. Smith is requesting a cardiology consult", "is_read": False},
            {"user": provider_user2, "type": "SYSTEM", "title": "Lab Results Available", "body": "New lab results are ready for review", "is_read": False},
        ]
        for n in notifications_data:
            notif = Notification(
                user_id=n["user"].id,
                type=n["type"],
                title=n["title"],
                body=n["body"],
                is_read=n["is_read"],
                read_at=n.get("read_at"),
                data_json={"test": True}
            )
            session.add(notif)
        print(f"  ✓ Notifications: 12 created (9 unread, 3 read)")

        # ============================================================
        # 12. MESSAGE THREADS
        # ============================================================
        print("Seeding message threads...")
        # Thread 1: Provider-Patient (Active, unread)
        thread1 = MessageThread(
            organization_id=org.id,
            subject="Lab Results Discussion",
            patient_id=patient_profile.id
        )
        session.add(thread1)
        await session.flush()
        
        # Participants for thread 1
        session.add(MessageParticipant(thread_id=thread1.id, user_id=provider_user.id, last_read_at=now()))
        session.add(MessageParticipant(thread_id=thread1.id, user_id=patient_user.id, last_read_at=now() - timedelta(days=1)))
        
        # Messages for thread 1
        session.add(Message(thread_id=thread1.id, sender_id=provider_user.id, body="Hi, I've reviewed your lab results. Everything looks good overall."))
        await session.flush()
        session.add(Message(thread_id=thread1.id, sender_id=patient_user.id, body="Thank you, doctor. Should I schedule a follow-up?"))
        await session.flush()
        session.add(Message(thread_id=thread1.id, sender_id=provider_user.id, body="Yes, please schedule one in 3 months. We'll recheck your cholesterol."))
        
        # Thread 2: Staff-Patient (Resolved, fully read)
        thread2 = MessageThread(
            organization_id=org.id,
            subject="Appointment Rescheduling",
            patient_id=patient_profile.id
        )
        session.add(thread2)
        await session.flush()
        
        # Participants for thread 2
        session.add(MessageParticipant(thread_id=thread2.id, user_id=staff_user.id, last_read_at=now()))
        session.add(MessageParticipant(thread_id=thread2.id, user_id=patient_user.id, last_read_at=now()))
        
        # Messages for thread 2
        session.add(Message(thread_id=thread2.id, sender_id=staff_user.id, body="Hi, we need to reschedule your upcoming appointment. What times work for you?"))
        await session.flush()
        session.add(Message(thread_id=thread2.id, sender_id=patient_user.id, body="Tuesday or Wednesday afternoon would work best. Thank you!"))
        print(f"  ✓ Message threads: 2 created with 5 messages total")

        # ============================================================
        # 13. SUPPORT TICKETS
        # ============================================================
        print("Seeding support tickets...")
        # Ticket 1: OPEN, HIGH, TECHNICAL
        ticket1 = SupportTicket(
            user_id=patient_user.id,
            organization_id=org.id,
            subject="Cannot access my test results",
            category="TECHNICAL",
            priority="HIGH",
            status="OPEN"
        )
        session.add(ticket1)
        await session.flush()
        session.add(SupportMessage(ticket_id=ticket1.id, sender_id=patient_user.id, body="I'm getting an error when trying to view my lab results. The page just shows a loading spinner."))
        
        # Ticket 2: IN_PROGRESS, MEDIUM, BILLING
        ticket2 = SupportTicket(
            user_id=patient_user.id,
            organization_id=org.id,
            subject="Billing question about recent visit",
            category="BILLING",
            priority="MEDIUM",
            status="IN_PROGRESS",
            assigned_to_id=staff_user.id
        )
        session.add(ticket2)
        await session.flush()
        session.add(SupportMessage(ticket_id=ticket2.id, sender_id=patient_user.id, body="I received a bill for my visit last week but my insurance should have covered it."))
        await session.flush()
        session.add(SupportMessage(ticket_id=ticket2.id, sender_id=staff_user.id, body="I'm looking into this for you. Can you provide your insurance policy number?"))
        await session.flush()
        session.add(SupportMessage(ticket_id=ticket2.id, sender_id=patient_user.id, body="Sure, it's POL-123456789."))
        
        # Ticket 3: RESOLVED, LOW, ACCOUNT
        ticket3 = SupportTicket(
            user_id=proxy_user.id,
            organization_id=org.id,
            subject="Need to update email address",
            category="ACCOUNT",
            priority="LOW",
            status="RESOLVED",
            assigned_to_id=staff_user.id,
            resolved_at=now() - timedelta(days=2)
        )
        session.add(ticket3)
        await session.flush()
        session.add(SupportMessage(ticket_id=ticket3.id, sender_id=proxy_user.id, body="I need to update my email address in the system."))
        await session.flush()
        session.add(SupportMessage(ticket_id=ticket3.id, sender_id=staff_user.id, body="Done! I've updated your email. Please verify you receive the confirmation.", is_internal=False))
        await session.flush()
        session.add(SupportMessage(ticket_id=ticket3.id, sender_id=staff_user.id, body="[Internal] Verified email change in admin panel.", is_internal=True))
        
        # Ticket 4: CLOSED, MEDIUM, OTHER
        ticket4 = SupportTicket(
            user_id=patient_user.id,
            organization_id=org.id,
            subject="General feedback",
            category="OTHER",
            priority="MEDIUM",
            status="CLOSED",
            resolved_at=now() - timedelta(days=5)
        )
        session.add(ticket4)
        await session.flush()
        session.add(SupportMessage(ticket_id=ticket4.id, sender_id=patient_user.id, body="Just wanted to say the new appointment booking feature is great!"))
        print(f"  ✓ Support tickets: 4 created with 8 messages (OPEN, IN_PROGRESS, RESOLVED, CLOSED)")

        # ============================================================
        # 14. CONSENT DOCUMENTS
        # ============================================================
        print("Seeding consent documents...")
        # Current active versions
        tos_current = ConsentDocument(doc_type="TOS", version="1.0", content_text="Terms of Service v1.0...", is_active=True)
        hipaa_current = ConsentDocument(doc_type="HIPAA", version="1.0", content_text="HIPAA Notice v1.0...", is_active=True)
        privacy_current = ConsentDocument(doc_type="PRIVACY", version="1.0", content_text="Privacy Policy v1.0...", is_active=True)
        # Old inactive version
        tos_old = ConsentDocument(doc_type="TOS", version="0.9", content_text="Terms of Service v0.9...", is_active=False)
        
        session.add_all([tos_current, hipaa_current, privacy_current, tos_old])
        await session.flush()
        
        # E2E user signs all active consents
        for doc in [tos_current, hipaa_current, privacy_current]:
            consent = UserConsent(
                user_id=e2e_user.id,
                document_id=doc.id,
                signed_at=now() - timedelta(days=30),
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Test)"
            )
            session.add(consent)
        print(f"  ✓ Consent documents: 4 created, 3 signed by E2E user")

        # ============================================================
        # 15. INVITATIONS
        # ============================================================
        print("Seeding invitations...")
        current_time = now()
        # Pending (valid)
        invite_pending = Invitation(
            organization_id=org.id,
            email="newstaff@example.com",
            role="STAFF",
            token=secrets.token_urlsafe(32),
            invited_by_user_id=e2e_user.id,
            status="PENDING",
            created_at=current_time,
            expires_at=current_time + timedelta(days=7)
        )
        session.add(invite_pending)
        
        # Pending (expired)
        invite_expired = Invitation(
            organization_id=org.id,
            email="lateprovider@example.com",
            role="PROVIDER",
            token=secrets.token_urlsafe(32),
            invited_by_user_id=e2e_user.id,
            status="PENDING",
            created_at=current_time - timedelta(days=10),
            expires_at=current_time - timedelta(days=3)
        )
        session.add(invite_expired)
        
        # Accepted
        invite_accepted = Invitation(
            organization_id=org.id,
            email="staff@example.com",
            role="STAFF",
            token=secrets.token_urlsafe(32),
            invited_by_user_id=e2e_user.id,
            status="ACCEPTED",
            created_at=current_time - timedelta(days=17),
            expires_at=current_time + timedelta(days=7),
            accepted_at=current_time - timedelta(days=10)
        )
        session.add(invite_accepted)
        print(f"  ✓ Invitations: 3 created (PENDING valid, PENDING expired, ACCEPTED)")

        # ============================================================
        # COMMIT ALL
        # ============================================================
        await session.commit()
        print("\n" + "="*60)
        print("✅ Database seeded successfully with all operational data!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(seed())