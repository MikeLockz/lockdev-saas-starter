import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/consent')({
  component: Consent,
})

function Consent() {
  return <div>Consent Page</div>
}
