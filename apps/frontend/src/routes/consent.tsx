import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { ConsentList } from '@/components/consent/ConsentList'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Shield } from 'lucide-react'

export const Route = createFileRoute('/consent')({
  component: ConsentPage,
})

function ConsentPage() {
  const navigate = useNavigate()

  const handleComplete = () => {
    navigate({ to: '/dashboard' })
  }

  return (
    <>
      <Header fixed>
        <h1 className="text-lg font-semibold">Consent Required</h1>
      </Header>

      <Main>
        <div className="max-w-3xl mx-auto space-y-6 py-8">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4">
                <Shield className="h-8 w-8 text-primary" />
                <div>
                  <CardTitle>Required Consent Documents</CardTitle>
                  <CardDescription>
                    Please review and accept the following documents to continue
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ConsentList onComplete={handleComplete} />
            </CardContent>
          </Card>
        </div>
      </Main>
    </>
  )
}
