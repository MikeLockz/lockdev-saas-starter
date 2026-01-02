import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/hooks/useAuth'
import { useEffect } from 'react'

export const Route = createFileRoute('/login')({
  component: Login,
})

function Login() {
  const { signInWithGoogle, signInDev, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) {
      navigate({ to: '/dashboard' })
    }
  }, [user, navigate])

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-[350px]">
        <CardHeader>
          <CardTitle>Login</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button className="w-full" onClick={() => signInWithGoogle()}>
            Sign in with Google
          </Button>

          {import.meta.env.DEV && (

            <div className="pt-4 border-t">
              <p className="text-xs text-muted-foreground mb-2 text-center">Dev Login</p>
              <div className="space-y-2">
                <Button variant="outline" className="w-full" onClick={() => signInDev('e2e@example.com', 'E2E User')}>
                  E2E User
                </Button>
                <Button variant="outline" className="w-full" onClick={() => signInDev('staff@example.com', 'Staff User')}>
                  Staff User
                </Button>
                <Button variant="outline" className="w-full" onClick={() => signInDev('patient@example.com', 'Patient User')}>
                  Patient User
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
