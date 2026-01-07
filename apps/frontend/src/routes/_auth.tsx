import { Outlet } from '@tanstack/react-router'
import { createFileRoute } from '@tanstack/react-router'
import { AuthGuard } from '@/components/auth-guard'
import { getCookie } from '@/lib/cookies'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/layout/app-sidebar'
import { useSessionMonitor } from '@/hooks/useSessionMonitor'
import { SessionExpiryModal } from '@/components/SessionExpiryModal'
import { useAuth } from '@/hooks/useAuth'

export const Route = createFileRoute('/_auth')({
  component: AuthLayout,
})

function AuthLayout() {
  const defaultOpen = getCookie('sidebar_state') !== 'false'
  const { showWarning, timeRemaining, extendSession } = useSessionMonitor()
  const { signOut } = useAuth()

  // Auto-logout is handled by the hook (isIdle -> signOut)
  // We just need to show the modal when warning is true

  return (
    <AuthGuard>
      <SidebarProvider defaultOpen={defaultOpen}>
        <AppSidebar />
        <SidebarInset>
          <Outlet />
        </SidebarInset>
        <SessionExpiryModal
          isOpen={showWarning}
          timeRemaining={timeRemaining}
          onExtend={extendSession}
          onLogout={signOut}
        />
      </SidebarProvider>
    </AuthGuard>
  )
}
