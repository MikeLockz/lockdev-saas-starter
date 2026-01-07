import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { type Session, useSessions } from "@/hooks/useSessions";

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString();
}

function SessionItem({
  session,
  onRevoke,
}: {
  session: Session;
  onRevoke: () => void;
}) {
  return (
    <div className="flex items-center justify-between p-4 rounded-lg border bg-card">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <span className="font-medium">{session.device}</span>
          {session.is_current && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary font-medium">
              Current
            </span>
          )}
        </div>
        <p className="text-sm text-muted-foreground">
          IP: {session.ip_address}
          {session.location && ` • ${session.location}`}
        </p>
        <p className="text-xs text-muted-foreground">
          Last active: {formatDate(session.last_active_at)}
        </p>
      </div>
      {!session.is_current && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRevoke}
          className="text-destructive hover:text-destructive"
        >
          Revoke
        </Button>
      )}
    </div>
  );
}

export function SessionList() {
  const { sessions, total, isLoading, revokeSession } = useSessions();

  const handleRevoke = async (sessionId: string) => {
    if (
      confirm(
        "Are you sure you want to revoke this session? This will sign out that device.",
      )
    ) {
      await revokeSession.mutateAsync(sessionId);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Active Sessions</CardTitle>
          <CardDescription>
            Devices currently signed into your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2].map((i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Active Sessions</CardTitle>
        <CardDescription>
          {total} device{total !== 1 ? "s" : ""} currently signed into your
          account
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {sessions.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">
            No active sessions
          </p>
        ) : (
          sessions.map((session) => (
            <SessionItem
              key={session.id}
              session={session}
              onRevoke={() => handleRevoke(session.id)}
            />
          ))
        )}
      </CardContent>
    </Card>
  );
}
