import { createFileRoute } from '@tanstack/react-router'
import { useAuth } from '@/hooks/useAuth'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
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
} from 'lucide-react'

export const Route = createFileRoute('/_auth/dashboard')({
  component: Dashboard,
})

const stats = [
  {
    title: 'Total Patients',
    value: '1,234',
    description: '+12% from last month',
    icon: Users,
  },
  {
    title: 'Appointments Today',
    value: '24',
    description: '8 remaining',
    icon: Calendar,
  },
  {
    title: 'Unread Messages',
    value: '7',
    description: '3 urgent',
    icon: MessageSquare,
  },
  {
    title: 'Active Sessions',
    value: '573',
    description: '+201 since last hour',
    icon: Activity,
  },
]

function Dashboard() {
  const { user } = useAuth()

  return (
    <>
      <Header fixed>
        <h1 className="text-lg font-semibold">Dashboard</h1>
        <div className="ml-auto flex items-center space-x-4">
          <span className="text-sm text-muted-foreground hidden sm:inline">
            Welcome back, {user?.displayName || user?.email?.split('@')[0] || 'User'}
          </span>
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
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <p className="text-xs text-muted-foreground">
                    {stat.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Main Content Grid */}
          <div className="grid gap-4 lg:grid-cols-7">
            {/* Overview Card */}
            <Card className="lg:col-span-4">
              <CardHeader>
                <CardTitle>Overview</CardTitle>
                <CardDescription>
                  Patient activity for the current month
                </CardDescription>
              </CardHeader>
              <CardContent className="h-[300px] flex items-center justify-center">
                <div className="flex flex-col items-center gap-2 text-muted-foreground">
                  <Activity className="h-12 w-12" />
                  <p className="text-sm">Activity chart will be displayed here</p>
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity Card */}
            <Card className="lg:col-span-3">
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                  Latest updates from your practice
                </CardDescription>
              </CardHeader>
              <CardContent>
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
              </CardContent>
            </Card>
          </div>
        </div>
      </Main>
    </>
  )
}
