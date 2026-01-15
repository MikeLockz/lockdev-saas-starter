# Frontend State Management Architecture

This document defines the architecture for the "Data Layer" of the frontend application, connecting UI Components to the Backend API using React Query for server state and Zustand for client state.

## Tech Stack Overview
- **Networking**: Axios (with interceptors for Auth, Impersonation, and Global Error Handling)
- **Server State**: @tanstack/react-query (v5)
- **Client State**: Zustand
- **Schema Validation**: Zod
- **Type Safety**: TypeScript (Synced with API Reference)

---

## 1. Core Networking Setup

We utilize a centralized Axios instance to handle authentication injection, base URL configuration, and global error normalization.

### `frontend/src/lib/axios.ts`

```typescript
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getAuth } from 'firebase/auth'; // Assuming Firebase Auth SDK
import { useAuthStore } from '@/store/auth-store';

// Base URL from environment or defaulting to local API
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

/**
 * Request Interceptor: Auto-inject Firebase Auth Token
 */
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // 1. Check for Active Impersonation Token first
    const { isImpersonating, impersonationToken } = useAuthStore.getState();
    
    if (isImpersonating && impersonationToken) {
       // Send the specific impersonation token (exchanged via /api/admin/impersonate)
       // This ensures the backend logs the action as "Admin acting as Target" via the `act_as` claim
       config.headers.Authorization = `Bearer ${impersonationToken}`;
    } else {
       // 2. Otherwise, use standard Firebase Auth
       const auth = getAuth();
       const user = auth.currentUser;
       if (user) {
         const token = await user.getIdToken();
         config.headers.Authorization = `Bearer ${token}`;
       }
    }

    // Inject Request ID for tracing
    config.headers['X-Request-ID'] = crypto.randomUUID(); 

    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response Interceptor: Global Error Handling
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // 401 Unauthorized
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      // Redirect handled by AuthGuard or router 
    }

    // 403 Forbidden
    if (error.response?.status === 403) {
      const code = error.response.data?.code;
      
      // HIPAA: Consent Required
      if (code === 'CONSENT_REQUIRED') {
         window.location.href = '/consent'; 
         return Promise.reject(error);
      }
      
      // HIPAA: MFA Enforcement
      if (code === 'MFA_REQUIRED') {
         window.location.href = '/settings/security/mfa?reason=required';
         return Promise.reject(error);
      }
      
      // Account Lockout or Security Issues
      if (code === 'ACCOUNT_LOCKED' || code === 'IMPERSONATION_EXPIRED') {
         useAuthStore.getState().logout();
         window.location.href = `/login?reason=${code.toLowerCase()}`;
         return Promise.reject(error);
      }
    }

    // 429 Rate Limit
    if (error.response?.status === 429) {
      // Use getState to access store outside React tree
      import('@/store/ui-store').then(({ useUIStore }) => {
        useUIStore.getState().showToast({ 
            type: 'error', 
            message: 'Too many requests. Please wait a moment.' 
        });
      });
    }
    
    return Promise.reject(error);
  }
);
```

### `frontend/src/lib/query-client.ts`

Configures React Query with sensible defaults for data freshness and error retry strategies.

```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1, // Retry failed requests once
      staleTime: 1000 * 60 * 5, // Data is fresh for 5 minutes
      refetchOnWindowFocus: false, // Prevent aggressive refetching
    },
    mutations: {
      retry: 0, // Do not retry mutations (writes) automatically to avoid duplicates
    },
  },
});
```

---

## 2. Client State (Zustand)

We use Zustand for global client-side state unrelated to API caching (e.g., active user session data that persists across views, UI themes).

### `frontend/src/store/auth-store.ts`

Stores the current user profile and critical session flags (MFA status, role).

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  mfa_enabled: boolean;
  requires_consent: boolean;
  roles: Array<{
    organization_id: string;
    role: 'PATIENT' | 'PROVIDER' | 'STAFF' | 'ADMIN' | 'SUPER_ADMIN';
  }>;
  // Profiles for specific access
  patient_profile?: {
      id: string;
      is_self_managed: boolean;
  };
  proxy_profile?: {
      id: string;
      managed_patients: Array<{ id: string; name: string }>;
  };
}

interface AuthState {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Impersonation State ("Break Glass")
  isImpersonating: boolean; 
  impersonationToken: string | null; // JWT with `act_as` claim
  originalAdminUser: UserProfile | null;
  
  // Actions
  setUser: (user: UserProfile) => void;
  setLoading: (loading: boolean) => void;
  setImpersonation: (active: boolean, token: string | null, targetUser: UserProfile | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      
      isImpersonating: false,
      impersonationToken: null,
      originalAdminUser: null,

      setUser: (user) => set({ user, isAuthenticated: true, isLoading: false }),
      setLoading: (loading) => set({ isLoading: loading }),
      
      // Updated to handle token storage
      setImpersonation: (active, token, targetUser) => set((state) => {
          if (active && targetUser && token) {
              return {
                  isImpersonating: true,
                  impersonationToken: token,
                  originalAdminUser: state.user, // Save admin
                  user: targetUser // Switch to target
              };
          } else {
              // Stop impersonation
              return {
                  isImpersonating: false,
                  impersonationToken: null,
                  user: state.originalAdminUser, // Revert
                  originalAdminUser: null
              };
          }
      }),

      logout: () => {
        sessionStorage.clear();
        set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false, 
            isImpersonating: false, 
            impersonationToken: null,
            originalAdminUser: null 
        });
      },
    }),
    {
      name: 'auth-storage', 
      storage: createJSONStorage(() => sessionStorage), // HIPAA: Clear on browser close
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated,
        isImpersonating: state.isImpersonating,
        impersonationToken: state.impersonationToken, 
        originalAdminUser: state.originalAdminUser 
      }),
    }
  )
);
```

### `frontend/src/store/ui-store.ts`

Manages ephemeral global UI state like Sidebar visibility, active Modals, and Toasts.

```typescript
import { create } from 'zustand';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastMessage {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface UIState {
  // Sidebar
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  
  // Toasts
  toasts: ToastMessage[];
  showToast: (toast: Omit<ToastMessage, 'id'>) => void;
  dismissToast: (id: string) => void;
  
  // Modals
  activeModal: string | null;
  openModal: (modalId: string) => void;
  closeModal: () => void;

  // Notification Panel
  isNotificationPanelOpen: boolean;
  toggleNotificationPanel: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  
  toasts: [],
  showToast: ({ type, message, duration = 5000 }) => {
    const id = crypto.randomUUID();
    set((state) => ({ toasts: [...state.toasts, { id, type, message, duration }] }));
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
    }, duration);
  },
  dismissToast: (id) => set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
  
  activeModal: null,
  openModal: (modalId) => set({ activeModal: modalId }),
  closeModal: () => set({ activeModal: null }),

  isNotificationPanelOpen: false,
  toggleNotificationPanel: () => set((state) => ({ isNotificationPanelOpen: !state.isNotificationPanelOpen })),
}));
```

---

## 3. Server State (React Query Hooks)

API interaction is encapsulated in custom hooks organized by domain. These hooks handle typing, error states, and cache invalidation.

### Domain Hook Strategy
To ensure consistency, all domain hooks must follow this pattern:
1.  **Strict Typing**: Use interfaces matching the Backend API.
2.  **Key Factories**: Define `queryKeys` objects for predictable cache management.
3.  **Invalidation Rules**: Mutations must invalidate relevant Lists or Details.
4.  **URL State Sync**: Critical for dashboards (Filters/Pagination). Hooks should consume `params` that drive from `useSearchParams`, not just local state.

### Required Domains (Scaffolded)
We require the following hook files corresponding to the core entities:
*   `usePatients.ts` (Managed Patients, Search)
*   `useAppointments.ts` (Scheduling, Rescheduling, Availability)
*   `useMessaging.ts` (Threads, Messages, Attachments)
*   `useDocuments.ts` (Uploads, Virus Scan Status, Shared Docs)
*   `useNotifications.ts` (Alerts, Read Status)
*   `useStaff.ts` (Providers, Admins, Organization Members)
*   `useCallCenter.ts` (Queue management, Active call state)
*   `useBilling.ts` (Invoices, Payment methods, Subscription status)
*   `useCompliance.ts` (Audit logs fetching, Export status)
*   `useSettings.ts` (MFA status, Communication preferences)
*   `useReferenceData.ts` (Static lists: States, Specialties)

### Domain Hook Example: `frontend/src/hooks/api/usePatients.ts`

Handles CRUD operations for Patients.

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/axios';

// --- Types (Should ideally match generated API types) ---
export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  dob: string;
  mrn: string;
  status: 'ACTIVE' | 'DISCHARGED';
  // ... other fields
}

export interface CreatePatientDTO {
  first_name: string;
  last_name: string;
  dob: string;
  // ...
}

export interface PatientsListParams {
  org_id: string;
  search?: string;
  status?: string;
  page?: number;
}

// --- Keys for Cache Management ---
export const patientKeys = {
  all: ['patients'] as const,
  lists: () => [...patientKeys.all, 'list'] as const,
  list: (params: PatientsListParams) => [...patientKeys.lists(), params] as const,
  details: () => [...patientKeys.all, 'detail'] as const,
  detail: (id: string) => [...patientKeys.details(), id] as const,
};

// --- Hooks ---

/**
 * Fetch list of patients for an organization
 */
export const usePatients = (params: PatientsListParams) => {
  return useQuery({
    queryKey: patientKeys.list(params),
    queryFn: async () => {
      const { data } = await apiClient.get<{ items: Patient[]; total: number }>(
        `/api/organizations/${params.org_id}/patients`,
        { params }
      );
      return data;
    },
    enabled: !!params.org_id, // Dependent query: only run if org_id exists
  });
};

/**
 * Fetch single patient details
 */
export const usePatient = (orgId: string, patientId: string) => {
  return useQuery({
    queryKey: patientKeys.detail(patientId),
    queryFn: async () => {
      const { data } = await apiClient.get<Patient>(
        `/api/organizations/${orgId}/patients/${patientId}`
      );
      return data;
    },
    enabled: !!orgId && !!patientId,
  });
};

/**
 * Create a new patient
 */
export const useCreatePatient = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ orgId, data }: { orgId: string; data: CreatePatientDTO }) => {
      const response = await apiClient.post<Patient>(
        `/api/organizations/${orgId}/patients`,
        data
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      // Invalidate list to show new patient
      queryClient.invalidateQueries({ queryKey: patientKeys.lists() });
      
      // Optional: Show Toast notification here via global UI store or callback
    },
  });
};
```

---

## 4. Integration & Security Logic

### `frontend/src/components/auth-guard.tsx`

This component protects routes based on authentication status that satisfies HIPAA requirements (MFA enforcement, Role-based access).

```tsx
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/auth-store';
import { Skeleton } from '@/components/ui/skeleton';

interface AuthGuardProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  requireMfa?: boolean;
}

export const AuthGuard = ({ children, allowedRoles, requireMfa = false }: AuthGuardProps) => {
  const { user, isAuthenticated, isLoading, isImpersonating } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // 1. Loading State Check
    if (isLoading) return;

    // 2. Authentication Check
    if (!isAuthenticated || !user) {
      navigate(`/login?redirect=${encodeURIComponent(location.pathname)}`, { replace: true });
      return;
    }

    // 3. User Role Check
    if (allowedRoles && allowedRoles.length > 0) {
      // If Impersonating, we bypass role check OR we check the *impersonated* user's role 
      // (usually we check the target user's role to see if they can view this page)
      const userHasRole = user.roles.some((r) => allowedRoles.includes(r.role));
      
      // Special Case: Impersonators might not have the "exact" role object in the same way, 
      // but usually the backend returns the "ACT_AS" user with their roles.
      if (!userHasRole) {
        navigate('/unauthorized', { replace: true }); 
        return;
      }
    }

    // 4. MFA Check (Critical for PHI Routes)
    // IMPERSONATION EXCEPTION: If isImpersonating, we assume the Admin already passed MFA.
    // However, the *target* user (Patient) might not have MFA.
    if (requireMfa && !isImpersonating && !user.mfa_enabled) {
      navigate('/settings/security/mfa?reason=required', { replace: true });
      return;
    }

    // 5. Consent Check
    if (user.requires_consent && location.pathname !== '/consent') {
      navigate('/consent', { replace: true });
      return;
    }

  }, [isLoading, isAuthenticated, user, navigate, allowedRoles, requireMfa, location, isImpersonating]);

  if (isLoading) {
    return <div className="p-10"><Skeleton className="h-[200px] w-full" /></div>;
  }

  // If we passed all checks, render view
  if (isAuthenticated && user) {
     const roleCheck = !allowedRoles || user.roles.some(r => allowedRoles.includes(r.role));
     // Allow MFA bypass if impersonating (Admin is trusted)
     const mfaCheck = !requireMfa || user.mfa_enabled || isImpersonating;
     
     if (roleCheck && mfaCheck) {
         return <>{children}</>;
     }
  }

  return null;
};
```

---

## 5. Wizard State Management

Complex multi-step flows (Onboarding, Proxy Invites, Appointment Scheduling) require state persistence across steps.

### Pattern: `useWizardStore` (Transient)

For long flows, do not rely solely on URL parameters. Use a transient Zustand store or React Context.

**Example: `frontend/src/features/onboarding/store.ts`**

```typescript
import { create } from 'zustand';

interface OnboardingData {
  displayName: string;
  phoneNumber: string;
  mfaVerified: boolean;
  selectedOrgId: string | null;
}

interface OnboardingState {
  currentStep: number;
  data: OnboardingData;
  setStep: (step: number) => void;
  updateData: (data: Partial<OnboardingData>) => void;
  reset: () => void;
}

export const useOnboardingStore = create<OnboardingState>((set) => ({
  currentStep: 1,
  data: {
    displayName: '',
    phoneNumber: '',
    mfaVerified: false,
    selectedOrgId: null,
  },
  setStep: (step) => set({ currentStep: step }),
  updateData: (updates) => set((state) => ({ data: { ...state.data, ...updates } })),
  reset: () => set({ currentStep: 1, data: { ... } }),
}));
```

### Recommendation
*   **Step Persistence**: If the wizard is critical, consider using `persist` (sessionStorage) so a page refresh doesn't lose progress.
*   **Cleanup**: Call `reset()` when the wizard successfully completes (e.g., in the `onSuccess` of the final mutation).

## 6. View Integration Example

How a View component consumes the data layer (Hooks + Guard).

**`frontend/src/features/patients/patient-detail-page.tsx`**

```tsx
import { useParams } from 'react-router-dom';
import { usePatient } from '@/hooks/api/usePatients';
import { AuthGuard } from '@/components/auth-guard';
import { Loader2 } from 'lucide-react';

export default function PatientDetailPage() {
  const { orgId, patientId } = useParams();
  
  // 1. Fetch Data
  const { data: patient, isLoading, error } = usePatient(orgId!, patientId!);

  if (isLoading) return <div className="flex justify-center p-12"><Loader2 className="animate-spin" /></div>;
  
  if (error) return <div className="text-red-500">Failed to load patient: {error.message}</div>;

  return (
    // 2. Security Wrapper
    <AuthGuard allowedRoles={['PROVIDER', 'STAFF']} requireMfa={true}>
      <div className="container mx-auto p-6">
        <h1 className="text-2xl font-bold">{patient?.first_name} {patient?.last_name}</h1>
        <p className="text-muted-foreground mr-4">MRN: {patient?.mrn}</p>
        
        {/* Render Tabs, etc. */}
      </div>
    </AuthGuard>
  );
}

---

## 6. Analytics

### `frontend/src/hooks/useAnalytics.ts`

Abstracts the telemetry API call to allow "fire and forget" tracking.

```typescript
import { apiClient } from '@/lib/axios';

export const useAnalytics = () => {
  const track = (eventName: string, properties: Record<string, any> = {}) => {
    // Fire and forget - don't block UI
    apiClient.post('/api/telemetry', { event_name: eventName, properties })
      .catch((err) => console.error('Telemetry failed:', err));
  };

  return { track };
};
```

---

## 7. Analytics

### `frontend/src/hooks/useAnalytics.ts`

Abstracts the telemetry API call to allow "fire and forget" tracking.

```typescript
import { apiClient } from '@/lib/axios';

export const useAnalytics = () => {
  const track = (eventName: string, properties: Record<string, any> = {}) => {
    // Fire and forget - don't block UI
    apiClient.post('/api/telemetry', { event_name: eventName, properties })
      .catch((err) => console.error('Telemetry failed:', err));
  };

  return { track };
};
```

---

## 8. Session Security (HIPAA)

### `frontend/src/hooks/useSessionMonitor.ts`

HIPAA §164.312(a)(2)(iii) requires automatic logoff after inactivity.

**Logic:**
1.  **Idle Timer**: Tracks `mousemove`, `keydown`, `click` events.
2.  **Warning**: After **13 minutes** of inactivity, shows a `SessionExpiryModal` (via `useUIStore`).
3.  **Logout**: After **15 minutes**, calls `useAuthStore.getState().logout()` and forces navigation to `/login?reason=timeout`.

```typescript
import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/store/auth-store';
import { useUIStore } from '@/store/ui-store';

const TIMEOUT_MS = 15 * 60 * 1000; // 15m
const WARNING_MS = 13 * 60 * 1000; // 13m

export const useSessionMonitor = () => {
    const { isAuthenticated, logout } = useAuthStore();
    const { openModal, closeModal } = useUIStore();
    const timeoutRef = useRef<NodeJS.Timeout>();
    const warningRef = useRef<NodeJS.Timeout>();

    useEffect(() => {
        if (!isAuthenticated) return;

        const resetTimer = () => {
            clearTimeout(timeoutRef.current);
            clearTimeout(warningRef.current);
            closeModal(); // If they move mouse during warning, close it

            warningRef.current = setTimeout(() => {
                openModal('session-warning'); 
            }, WARNING_MS);

            timeoutRef.current = setTimeout(() => {
                logout();
                window.location.href = '/login?reason=timeout';
            }, TIMEOUT_MS);
        };

        const events = ['mousemove', 'keydown', 'click', 'scroll'];
        events.forEach(e => window.addEventListener(e, resetTimer));
        
        resetTimer(); // Start

        return () => {
            events.forEach(e => window.removeEventListener(e, resetTimer));
            clearTimeout(timeoutRef.current);
            clearTimeout(warningRef.current);
        };
    }, [isAuthenticated, logout, openModal, closeModal]);
};
```
