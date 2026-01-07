import { createFileRoute, Link } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/')({
  component: Index,
})

function Index() {
  return (
    <div className="p-8 flex flex-col gap-4 items-center">
      <h3 className="text-2xl font-bold">Welcome to Lockdev SaaS</h3>
      <div className="flex gap-4">
        <Link to="/login">
            <Button>Login</Button>
        </Link>
        <Link to="/dashboard">
            <Button variant="outline">Go to Dashboard</Button>
        </Link>
      </div>
    </div>
  )
}
