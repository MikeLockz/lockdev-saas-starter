# Data Model: Initial SaaS Starter MVP Platform

## ER Diagram (Mermaid)

```mermaid
erDiagram
    Tenant ||--|{ User : "has staff"
    Tenant ||--|{ Patient : "manages"
    User ||--o{ AuditLog : "generates"
    User ||--|{ Message : "sends"
    Patient ||--|{ Document : "owns"
    Patient ||--o{ Subscription : "has"
    Patient ||--|{ Message : "receives/sends"
    Subscription ||--|{ Payment : "has"

    Tenant {
        uuid id PK
        string name
        datetime created_at
        boolean is_active
    }

    User {
        uuid id PK
        uuid tenant_id FK
        string email
        string hashed_password
        string role "SUPER_ADMIN, TENANT_ADMIN, AGENT"
        string full_name
        datetime created_at
    }

    Patient {
        uuid id PK
        uuid tenant_id FK
        uuid user_id FK "Optional link if patient logs in"
        string healthie_id "External Ref"
        string first_name
        string last_name
        date dob
        string email
        string phone
        jsonb medical_history "Extracted Data"
        datetime created_at
    }

    Document {
        uuid id PK
        uuid patient_id FK
        string s3_key
        string filename
        string status "PENDING, PROCESSED, FAILED"
        datetime uploaded_at
    }

    Subscription {
        uuid id PK
        uuid patient_id FK
        string stripe_subscription_id
        string status "ACTIVE, CANCELED, PAST_DUE"
        date current_period_start
        date current_period_end
    }

    Payment {
        uuid id PK
        uuid subscription_id FK
        decimal amount
        string currency
        string status
        datetime transaction_date
    }

    Message {
        uuid id PK
        uuid tenant_id FK
        uuid sender_id FK "User or Patient"
        uuid recipient_id FK
        text content "Encrypted"
        datetime sent_at
        boolean is_read
    }

    AuditLog {
        uuid id PK
        uuid tenant_id FK
        uuid actor_id FK
        string action
        string resource_type
        uuid resource_id
        jsonb changes
        datetime timestamp
    }
```

## Entity Details

### Tenant
- **Purpose**: Logical isolation boundary.
- **RLS**: All other tables (except Super Admin data) must have `tenant_id` and RLS enabled.

### User
- **Roles**:
    - `SUPER_ADMIN`: Cross-tenant access (system maintenance).
    - `TENANT_ADMIN`: Manage users within their tenant.
    - `AGENT`: Read/Write patients, handle tasks.

### Patient
- **Data**: Core demographic data.
- **Sync**: `healthie_id` stores the reference to the external EHR record.
- **Security**: Name, DOB, Phone are PII/PHI - must be encrypted at rest if not relying solely on volume encryption.

### Message
- **Compliance**: Content must be encrypted.
- **Retention**: Permanent retention in DB for audit.

### Document
- **Storage**: Metadata in DB, binary content in private S3 bucket (SSE-KMS encrypted).
