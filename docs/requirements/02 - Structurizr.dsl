workspace "Healthcare SaaS Platform" "A HIPAA-compliant, AI-native care coordination platform." {

    model {
        # ---------------------------------------------------------------------
        # Actors (Users)
        # ---------------------------------------------------------------------
        patient = person "Patient" "Receives care. Data subject."
        proxy = person "Care Proxy" "Family/Guardian managing care for one or more patients."
        agent = person "Call Center Agent" "Manages patient queues and workflows."
        admin = person "Platform Admin" "System config & tenant management."

        # ---------------------------------------------------------------------
        # External Systems (Integrations & Infra)
        # ---------------------------------------------------------------------
        group "Google Cloud Platform" {
            gcpAuth = softwareSystem "Identity Platform" "Handles OIDC authentication, MFA & session management." "External"
        }

        group "AWS Services" {
            vertex = softwareSystem "Google Vertex AI" "LLM (Gemini) for summarization & intent detection." "External"
            ses = softwareSystem "AWS SES" "Transactional Email Service." "External"
            s3 = softwareSystem "AWS S3" "Private, Encrypted Object Storage." "External"
            connect = softwareSystem "Amazon Connect" "IVR & Contact Center flows." "External"
            messaging = softwareSystem "AWS End User Messaging" "Transactional SMS." "External"
        }

        # ---------------------------------------------------------------------
        # The System Boundary
        # ---------------------------------------------------------------------
        healthcareSystem = softwareSystem "Healthcare SaaS Platform" "Orchestrates multi-tenant care workflows." {

            # Presentation Layer
            mobileApp = container "Mobile App" "Patient & Proxy interface." "Capacitor + React" "Mobile"
            webApp = container "Web Dashboard" "Agent/Admin interface." "Vite + React" "Browser"

            # Application Layer
            api = container "API Application" "Business logic, HIPAA compliance (Audit/Masking), Tenant isolation." "Python 3.11, FastAPI" "API"
            worker = container "Background Worker" "Async processing (AI, Email, Reports)." "Python, Arq" "Worker"

            # Data Layer (Aptible Managed)
            database = container "Primary Database" "Stores patient data, audit logs." "PostgreSQL (Aptible)" "Database"
            redis = container "Cache & Queue" "Job queue for Arq, caching." "Redis (Aptible)" "Database"

            # -----------------------------------------------------------------
            # Internal Relationships
            # -----------------------------------------------------------------
            # User -> UI
            patient -> mobileApp "Views care plans, chats"
            proxy -> mobileApp "Manages dependents"
            agent -> webApp "Manages queues"
            admin -> webApp "Configures tenants"

            # UI -> API
            mobileApp -> api "JSON/HTTPS" "TanStack Query"
            webApp -> api "JSON/HTTPS" "TanStack Query"

            # API -> Backing Services
            api -> database "Reads/Writes" "SQLAlchemy/AsyncPG"
            api -> redis "Enqueues jobs" "Arq"
            api -> gcpAuth "Verifies Tokens" "Firebase Admin SDK"
            api -> s3 "Generates Pre-signed URLs" "Boto3"
            
            # API -> External Integrations
            api -> connect "Controls calls" "Boto3 (Connect)"
            api -> messaging "Sends SMS" "Boto3 (Pinpoint/SMS)"
            api -> ehr "Syncs data" "FHIR/HL7"
            api -> ehr "Syncs data" "FHIR/HL7"

            # Worker Logic
            worker -> redis "Dequeues jobs" "Arq"
            worker -> database "Reads/Writes" "SQLAlchemy"
            worker -> vertex "Sends prompts" "Google Cloud SDK"
            worker -> ses "Sends emails" "Boto3"
            worker -> s3 "Processes files" "Boto3"
        }
    }

    # -------------------------------------------------------------------------
    # Views & Styling
    # -------------------------------------------------------------------------
    views {
        # Level 1: Context
        systemContext healthcareSystem "SystemContext" {
            include *
            autoLayout
        }

        # Level 2: Container
        container healthcareSystem "Containers" {
            include *
            autoLayout
        }

        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #2fa434
            }
            element "Mobile" {
                shape MobileDeviceLandscape
            }
            element "Browser" {
                shape WebBrowser
            }
            element "API" {
                shape Hexagon
            }
            element "Worker" {
                shape Robot
            }
        }
    }
}
