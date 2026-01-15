Create 08 - front end state management.md

#Role: 
You are a Senior Frontend Architect and React Specialist. Your goal is to create the requirements to define how to "wire up" the frontend application by creating the state management layer that connects the UI Components to the Backend API. You are creating a technical document.

## Input Context
You have access to the following project documentation which act as your source of truth:
1.  **Components Inventory**: @07 - front end components.md  - Defines the UI components and structure.
2.  **API Schema**: @05 - API Reference.md  - Defines the data source, endpoints, and response shapes.
3.  **Authentication & Routing**: @06 - Frontend Views & Routes.md  - Defines the flows, role-based access control, and UI states.

## Technology Stack
- **Framework**: React (Vite) + TypeScript
- **Server State**: @tanstack/react-query (v5)
- **Client State**: Zustand
- **Data Fetching**: Axios
- **Validation/Typing**: Zod + OpenAPI generated types (prefer generated types from `frontend/src/lib/api-types.d.ts` if available, otherwise define matching interfaces based on `docs/05`).

## Objectives
Your task is to generate the code for the "Data Layer" of the frontend. You are NOT responsible for building CSS/UI layouts (those are handled by the Component/View implementation), but you ARE responsible for logic hooks that power those views.

### 1. Core Networking Setup
- **Axios Client**: Ensure `frontend/src/lib/axios.ts` is configured with:
    - Base URL from environment variables.
    - **Request Interceptor**: Auto-inject `Authorization: Bearer <token>` using the Firebase Auth token.
    - **Response Interceptor**: Global error handling (e.g., redirect to `/login` on 401, show Toast on 500).
    - **Domain Whitelisting**: As specified in the Implementation Plan.

### 2. State Management Architecture
- **Global Store (Zustand)**: Create `frontend/src/store/` for specific client-only state:
    - `useAuthStore`: Stores current user profile, roles, and session status.
    - `useUIStore`: Sidebar state, theme configurations, active modals.
- **Server State (React Query)**: Create `frontend/src/hooks/api/` organized by domain (matching API sections):
    - `useAuth` (User profile, session management)
    - `usePatients` (CRUD, lists, search)
    - `useAppointments` (Booking, rescheduling, lists)
    - `useMessages` (Inbox, thread, sending)
    - `useDocuments` (Uploads, listings)

### 3. Hook Requirements
For each data hook (e.g., `usePatient(id)`), ensure you implement:
- **Type Safety**: Strictly typed arguments and return values.
- **Loading States**: Return `isLoading` / `isPending` status.
- **Error Handling**: Return typed errors that match `docs/05` error codes.
- **Cache Invalidation**: On mutations (e.g., `updatePatient`), automatically invalidate relevant queries (e.g., `['patient', id]`).
- **Data Transformation**: If necessary, allow generic selectors to transform data before it reaches the component.

### 4. Integration Logic
- **Auth Guard**: Create a `RequireAuth` wrapper component that checks:
    1. Is user logged in?
    2. Does user have the required Role? (Compare against `docs/06` permission matrix)
    3. Is MFA required and enabled?
    - If any fail, redirect appropriately (e.g., to `/login` or `/unauthorized`).
- **Context Wiring**: Ensure `QueryClientProvider` is at the root.

## Instructions for Execution
When generating code, follow this sequence:
1.  **Setup the Core**: Write `axios.ts` and `query-client.ts`.
2.  **Define Types**: Create/Update TypeScript interfaces to match `docs/05 - API Reference.md` exactly.
3.  **Create Custom Hooks**: precise hooks for the critical paths defined in `docs/06` (e.g., `useSubmitConsent`, `useImpersonatePatient`).
4.  **View Integration Examples**: Show how a View component (e.g., `PatientDetailView`) should consume these hooks.

## Deliverables
Produce the code files for:
- `frontend/src/lib/axios.ts`
- `frontend/src/lib/query-client.ts`
- `frontend/src/store/auth-store.ts`
- `frontend/src/hooks/api/usePatients.ts` (Example of domain hook)
- `frontend/src/components/auth-guard.tsx`

Strictly adhere to the patterns defined in the inputs. Do not hallucinate endpoints that do not exist in `docs/05`.


Create the technical document that outlines the state management layer for the frontend application and write to markdown file.