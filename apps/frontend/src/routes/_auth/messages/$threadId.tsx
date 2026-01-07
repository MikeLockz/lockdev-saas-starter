import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_auth/messages/$threadId')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_auth/messages/$threadId"!</div>
}
