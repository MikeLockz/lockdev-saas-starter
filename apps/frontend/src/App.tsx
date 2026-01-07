import { useState } from "react";
import viteLogo from "/vite.svg";
import reactLogo from "./assets/react.svg";
import "./App.css";
import { toast } from "sonner";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Toaster } from "@/components/ui/sonner";
import { useAuth } from "@/hooks/useAuth";

function App() {
  const [count, setCount] = useState(0);
  const { user, signInWithGoogle, signOut } = useAuth();

  return (
    <>
      <Toaster />
      <div className="flex justify-center gap-4 mb-4">
        <a href="https://vite.dev" target="_blank" rel="noreferrer noopener">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" rel="noreferrer noopener">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1 className="mb-4 text-2xl font-bold">Vite + React + Shadcn UI</h1>

      <div className="grid gap-4 max-w-md mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Auth Test</CardTitle>
          </CardHeader>
          <CardContent>
            {user ? (
              <div className="flex flex-col gap-2">
                <p>Signed in as: {user.email}</p>
                <Button variant="outline" onClick={() => signOut()}>
                  Sign Out
                </Button>
              </div>
            ) : (
              <Button onClick={() => signInWithGoogle().catch(console.error)}>
                Sign In with Google
              </Button>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Interactive Components</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <div className="flex items-center gap-4">
              <Avatar>
                <AvatarImage src="https://github.com/shadcn.png" />
                <AvatarFallback>CN</AvatarFallback>
              </Avatar>
              <div className="space-y-1">
                <p className="text-sm font-medium leading-none">Shadcn</p>
                <p className="text-sm text-muted-foreground">Components</p>
              </div>
            </div>

            <div className="flex gap-2">
              <Input placeholder="Type something..." />
              <Button
                onClick={() => {
                  setCount((count) => count + 1);
                  toast("Button clicked!", {
                    description: `Count is now ${count + 1}`,
                  });
                }}
              >
                Count is {count}
              </Button>
            </div>

            <div className="space-y-2">
              <Skeleton className="h-4 w-[250px]" />
              <Skeleton className="h-4 w-[200px]" />
            </div>
          </CardContent>
        </Card>
      </div>

      <p className="mt-4 text-muted-foreground">
        Edit <code>src/App.tsx</code> and save to test HMR
      </p>
    </>
  );
}

export default App;
