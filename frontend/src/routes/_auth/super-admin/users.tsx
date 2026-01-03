import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_auth/super-admin/users')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_auth/super-admin/users"!</div>
}
