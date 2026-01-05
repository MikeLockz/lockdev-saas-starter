import { createFileRoute } from '@tanstack/react-router'
import { useAuth } from '@/hooks/useAuth'
import { useCurrentUser } from '@/hooks/api/useCurrentUser'
import { useOrganizations } from '@/hooks/api/useOrganizations'
import { useTodaysAppointmentsCount, useUnreadCount, useActiveSessionsCount } from '@/hooks/api/useDashboardStats'
import { useUserRole } from '@/hooks/useUserRole'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProviderOverviewCard } from '@/components/dashboard/ProviderOverviewCard'
import { PatientOverviewCard } from '@/components/dashboard/PatientOverviewCard'
import { StaffOverviewCard } from '@/components/dashboard/StaffOverviewCard'
import { SuperAdminOverviewCard } from '@/components/dashboard/SuperAdminOverviewCard'
import { ProxyOverviewCard } from '@/components/dashboard/ProxyOverviewCard'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Users,
  Calendar,
  MessageSquare,
  Activity,
  AlertCircle,
} from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_auth/dashboard')({
  component: Dashboard,
})

function Dashboard() {
  const { user: firebaseUser } = useAuth()
  const { data: currentUser, isLoading: isUserLoading, error: userError, refetch: refetchUser } = useCurrentUser()
  const { data: organizations, isLoading: isOrgsLoading, error: orgsError, refetch: refetchOrgs } = useOrganizations()
  const { data: appointmentsToday, isLoading: isApptsLoading } = useTodaysAppointmentsCount()
  const { data: unreadNotifications, isLoading: isNotifLoading } = useUnreadCount()
  const { data: activeSessions, isLoading: isSessionsLoading } = useActiveSessionsCount()
  const { roleInfo, isLoading: isRoleLoading } = useUserRole()

  const isLoading = isUserLoading || isOrgsLoading || isRoleLoading
  const hasError = userError || orgsError

  // Derive display name from API data first, fallback to Firebase
  const displayName = currentUser?.display_name ||
    firebaseUser?.displayName ||
    firebaseUser?.email?.split('@')[0] ||
    'User'

  // Stats derived from real data where available
  const stats = [
    {
      title: 'Organizations',
      value: isLoading ? '-' : (organizations?.length?.toString() || '0'),
      description: 'Active organizations',
      icon: Users,
    },
    {
      title: 'Appointments Today',
      value: isApptsLoading ? '-' : (appointmentsToday?.toString() ?? '0'),
      description: 'Scheduled & confirmed',
      icon: Calendar,
    },
    {
      title: 'Unread Notifications',
      value: isNotifLoading ? '-' : (unreadNotifications?.count?.toString() ?? '0'),
      description: 'Across all types',
      icon: MessageSquare,
    },
    {
      title: 'Active Sessions',
      value: isSessionsLoading ? '-' : (activeSessions?.toString() ?? '0'),
      description: 'Your login sessions',
      icon: Activity,
    },
  ]

  if (hasError) {
    return (
      <>
        <Header fixed>
          <h1 className="text-lg font-semibold">Dashboard</h1>
        </Header>
        <Main>
          <div className="flex flex-col items-center justify-center gap-4 py-12">
            <AlertCircle className="h-12 w-12 text-destructive" />
            <h2 className="text-lg font-semibold">Failed to load dashboard</h2>
            <p className="text-muted-foreground">
              {userError?.message || orgsError?.message || 'An error occurred'}
            </p>
            <Button onClick={() => { refetchUser(); refetchOrgs(); }}>
              Try Again
            </Button>
          </div>
        </Main>
      </>
    )
  }

  return (
    <>
      <Header fixed>
        <h1 className="text-lg font-semibold">Dashboard</h1>
        <div className="ml-auto flex items-center space-x-4">
          {isLoading ? (
            <Skeleton className="h-4 w-32" />
          ) : (
            <span className="text-sm text-muted-foreground hidden sm:inline">
              Welcome back, {displayName}
            </span>
          )}
        </div>
      </Header>

      <Main>
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat) => (
              <Card key={stat.title}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {stat.title}
                  </CardTitle>
                  <stat.icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <>
                      <Skeleton className="h-8 w-16 mb-1" />
                      <Skeleton className="h-3 w-24" />
                    </>
                  ) : (
                    <>
                      <div className="text-2xl font-bold">{stat.value}</div>
                      <p className="text-xs text-muted-foreground">
                        {stat.description}
                      </p>
                    </>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Main Content Grid */}
          <div className="grid gap-4 lg:grid-cols-7">
            {/* Overview Card - Role-specific or generic */}
            {roleInfo?.role === 'super_admin' ? (
              <SuperAdminOverviewCard />
            ) : roleInfo?.role === 'provider' && roleInfo.providerId ? (
              <ProviderOverviewCard
                providerId={roleInfo.providerId}
                userId={currentUser?.id || ''}
              />
            ) : roleInfo?.role === 'patient' && roleInfo.patientId ? (
              <PatientOverviewCard
                patientId={roleInfo.patientId}
              />
            ) : roleInfo?.role === 'staff' && roleInfo.staffId ? (
              <StaffOverviewCard
                staffId={roleInfo.staffId}
                userId={currentUser?.id || ''}
                jobTitle={null}
                department={null}
              />
            ) : roleInfo?.role === 'proxy' && roleInfo.proxyId ? (
              <ProxyOverviewCard proxyId={roleInfo.proxyId} />
            ) : (
              <Card className="lg:col-span-4">
                <CardHeader>
                  <CardTitle>Overview</CardTitle>
                  <CardDescription>
                    Activity for the current month
                  </CardDescription>
                </CardHeader>
                <CardContent className="h-[300px] flex items-center justify-center">
                  <div className="flex flex-col items-center gap-2 text-muted-foreground">
                    <Activity className="h-12 w-12" />
                    <p className="text-sm">Activity chart will be displayed here</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recent Activity Card */}
            <Card className="lg:col-span-3">
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                  Latest updates from your practice
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <div key={i} className="flex items-center gap-4">
                        <Skeleton className="h-9 w-9 rounded-full" />
                        <div className="flex-1 space-y-2">
                          <Skeleton className="h-4 w-24" />
                          <Skeleton className="h-3 w-32" />
                        </div>
                        <Skeleton className="h-3 w-16" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {[
                      { name: 'John Smith', action: 'Appointment completed', time: '2 min ago' },
                      { name: 'Sarah Johnson', action: 'New message received', time: '15 min ago' },
                      { name: 'Mike Davis', action: 'Document uploaded', time: '1 hour ago' },
                      { name: 'Emily Brown', action: 'Appointment scheduled', time: '2 hours ago' },
                      { name: 'Robert Wilson', action: 'Prescription renewed', time: '3 hours ago' },
                    ].map((activity, index) => (
                      <div key={index} className="flex items-center gap-4">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-muted">
                          <span className="text-sm font-medium">
                            {activity.name.charAt(0)}
                          </span>
                        </div>
                        <div className="flex-1 space-y-1">
                          <p className="text-sm font-medium leading-none">
                            {activity.name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {activity.action}
                          </p>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {activity.time}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </Main>
    </>
  )
}
