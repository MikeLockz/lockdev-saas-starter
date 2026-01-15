workspace "Lockdev" "HIPAA-Compliant Healthcare SaaS Platform" {

    !identifiers hierarchical

    model {
        # ============================================================================
        # PEOPLE (Actors)
        # ============================================================================
        patient = person "Patient" "End user accessing their health data via web/mobile" {
            tags "User"
        }
        
        staff = person "Staff" "Healthcare professional or admin managing patient care" {
            tags "User" "Internal"
        }
        
        callAgent = person "Call Center Agent" "Handles patient calls and manages communications" {
            tags "User" "Internal"
        }
        
        superAdmin = person "Super Admin" "Platform administrator managing organizations" {
            tags "User" "Admin"
        }

        # ============================================================================
        # EXTERNAL SYSTEMS
        # ============================================================================
        firebase = softwareSystem "Firebase/GCIP" "Cloud Identity Platform for authentication with MFA" {
            tags "External" "Auth"
        }
        
        stripe = softwareSystem "Stripe" "Payment processing and subscription management" {
            tags "External" "Payments"
        }
        
        aws = softwareSystem "AWS Services" "S3, SES, Textract, CloudWatch" {
            tags "External" "Cloud"
        }
        
        vertexAI = softwareSystem "Vertex AI" "Google Cloud AI for document processing and summaries" {
            tags "External" "AI"
        }
        
        sentry = softwareSystem "Sentry" "Error tracking and APM" {
            tags "External" "Observability"
        }

        # ============================================================================
        # LOCKDEV PLATFORM (Our System)
        # ============================================================================
        lockdev = softwareSystem "Lockdev Platform" "Multi-tenant healthcare SaaS with HIPAA compliance" {
            tags "Primary"
            
            # --------------------------------------------------------------------
            # CONTAINERS
            # --------------------------------------------------------------------
            spa = container "Single Page App" "React + TanStack Router/Query + Zustand" "TypeScript" {
                tags "Frontend" "Web"
                description "Progressive Web App for patients, staff, and admins"
            }
            
            api = container "API Server" "FastAPI with async SQLAlchemy" "Python 3.11" {
                tags "Backend" "API"
                description "RESTful API with JWT auth, rate limiting, audit logging"
                
                # Components within API
                authModule = component "Auth Module" "Firebase token verification, session management"
                consentModule = component "Consent Module" "HIPAA consent handling"
                userModule = component "User Module" "User CRUD operations"
                orgModule = component "Organization Module" "Multi-tenant organization management"
                billingModule = component "Billing Module" "Stripe subscription handling"
                documentsModule = component "Documents Module" "S3 upload, Textract processing"
                eventsModule = component "Events Module" "SSE real-time updates"
                telemetryModule = component "Telemetry Module" "Behavioral analytics"
            }
            
            worker = container "Background Worker" "ARQ (async Redis queue)" "Python 3.11" {
                tags "Backend" "Worker"
                description "Async job processing for emails, documents, scheduled tasks"
            }
            
            db = container "Database" "PostgreSQL 15 with RLS" "SQL" {
                tags "Storage" "Database"
                description "Primary data store with row-level security for tenant isolation"
            }
            
            cache = container "Cache/Queue" "Redis 7" "NoSQL" {
                tags "Storage" "Cache"
                description "Session cache, rate limiting, job queue, pub/sub"
            }
        }

        # ============================================================================
        # RELATIONSHIPS
        # ============================================================================
        
        # User relationships
        patient -> spa "Uses" "HTTPS"
        staff -> spa "Uses" "HTTPS"
        callAgent -> spa "Uses" "HTTPS"
        superAdmin -> spa "Uses" "HTTPS"
        
        # SPA relationships
        spa -> api "API Calls" "HTTPS/JSON"
        spa -> firebase "Authentication" "Firebase SDK"
        
        # API relationships
        api -> db "Reads/Writes" "asyncpg"
        api -> cache "Sessions/Rate Limits/Jobs" "redis-py"
        api -> firebase "Token Verification" "Admin SDK"
        api -> stripe "Payments" "Stripe API"
        api -> aws "Documents/Email/Logs" "boto3"
        api -> vertexAI "AI Processing" "Vertex SDK"
        api -> sentry "Error Tracking" "Sentry SDK"
        
        # Worker relationships
        worker -> db "Reads/Writes" "asyncpg"
        worker -> cache "Job Queue" "ARQ"
        worker -> aws "Document Processing" "boto3"
        worker -> vertexAI "Text Analysis" "Vertex SDK"
        
        # Internal container relationships
        api -> worker "Enqueue Jobs" "Redis Pub/Sub"
        worker -> api "Publish Events" "Redis Pub/Sub"
    }

    # ============================================================================
    # VIEWS
    # ============================================================================
    views {
        # Level 1: System Context
        systemContext lockdev "L1-SystemContext" {
            title "Lockdev System Context (L1)"
            description "High-level view of Lockdev and its external dependencies"
            include *
            autoLayout
        }
        
        # Level 2: Container View
        container lockdev "L2-ContainerView" {
            title "Lockdev Container View (L2)"
            description "Internal containers of the Lockdev Platform"
            include *
            autoLayout
        }
        
        # Level 3: Component View - API
        component api "L3-APIComponents" {
            title "API Server Components (L3)"
            description "Key modules within the FastAPI backend"
            include *
            autoLayout
        }
        
        # Dynamic View: Patient Registration Flow
        dynamic lockdev "PatientRegistration" {
            title "Patient Registration Flow"
            description "Shows the authentication and consent flow for new patients"
            patient -> spa "Opens app"
            spa -> firebase "Authenticates"
            firebase -> spa "Returns JWT"
            spa -> api "GET /api/user/me"
            api -> spa "requires_consent: true"
            spa -> api "POST /api/consent"
            api -> db "Store consent"
            api -> spa "OK"
            autoLayout
        }

        # Styles
        styles {
            element "User" {
                shape Person
                background #08427B
                color #ffffff
            }
            element "Internal" {
                background #1168BD
            }
            element "Admin" {
                background #6B1168
            }
            element "Primary" {
                background #1168BD
                color #ffffff
            }
            element "Frontend" {
                shape WebBrowser
                background #438DD5
                color #ffffff
            }
            element "Backend" {
                shape Hexagon
                background #438DD5
                color #ffffff
            }
            element "Storage" {
                shape Cylinder
                background #438DD5
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Auth" {
                background #FF9900
            }
            element "Payments" {
                background #635BFF
            }
            element "Cloud" {
                background #FF9900
            }
            element "AI" {
                background #4285F4
            }
            element "Observability" {
                background #362D59
            }
            relationship "Relationship" {
                dashed false
            }
        }
    }
}
