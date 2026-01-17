workspace "Healthcare SaaS Platform" "A HIPAA-compliant, AI-native care coordination platform." {

    model {
        # ---------------------------------------------------------------------
        # Actors (Users)
        # ---------------------------------------------------------------------
        patient = person "Patient" "Receives care. Data subject."
        proxy = person "Care Proxy" "Family/Guardian managing care for one or more patients."
        staff = person "Care Staff" "Manages patient workflows."
        admin = person "Platform Admin" "System config & tenant management."

        # ---------------------------------------------------------------------
        # External Systems (Integrations & Infra)
        # ---------------------------------------------------------------------
        group "Google Cloud Platform" {
            firebase = softwareSystem "Firebase Auth" "Handles OIDC authentication & MFA." "External"
            vertexai = softwareSystem "Vertex AI" "Gemini 1.5 for summarization." "External"
        }

        group "External Providers" {
            stripe = softwareSystem "Stripe" "Handles billing and subscriptions." "External"
        }

        group "AWS Services" {
            ses = softwareSystem "AWS SES" "Transactional Email Service." "External"
            s3 = softwareSystem "AWS S3" "Private, Encrypted Object Storage." "External"
            pinpoint = softwareSystem "AWS Pinpoint" "SMS and Notifications." "External"
        }

        # ---------------------------------------------------------------------
        # The System Boundary
        # ---------------------------------------------------------------------
        healthcareSystem = softwareSystem "Healthcare SaaS Platform" "Orchestrates multi-tenant care workflows." {

            # Presentation Layer
            webApp = container "Web Dashboard" "React/Vite SPA." "Vite + React" "Browser"

            # Application Layer
            api = container "API Application" "Business logic, HIPAA compliance, Tenant isolation." "Python 3.11, FastAPI" "API"
            worker = container "Background Worker" "Async processing (AI, Email)." "Python, Arq" "Worker"

            # Data Layer
            database = container "Primary Database" "Stores domain data, audit logs." "PostgreSQL" "Database"
            redis = container "Cache & Queue" "Job queue for Arq." "Redis" "Database"

            # -----------------------------------------------------------------
            # Internal Relationships
            # -----------------------------------------------------------------
            patient -> webApp "Uses"
            staff -> webApp "Uses"
            admin -> webApp "Uses"

            webApp -> api "JSON/HTTPS"

            api -> database "Reads/Writes"
            api -> redis "Enqueues"
            api -> firebase "Verifies"
            api -> vertexai "Sends prompts"
            api -> stripe "Manages billing"
            
            worker -> redis "Dequeues"
            worker -> database "Reads/Writes"
            worker -> vertexai "Summarizes"
            worker -> ses "Sends emails"
        }
    }

    views {
        systemContext healthcareSystem "SystemContext" {
            include *
            autoLayout
        }

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