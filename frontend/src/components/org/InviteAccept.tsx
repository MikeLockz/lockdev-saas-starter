
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../ui/card";
import { useInvitation } from "../../hooks/useInvitation";
import { useAcceptInvitation } from "../../hooks/useAcceptInvitation";
import { useNavigate } from "@tanstack/react-router";

interface InviteAcceptProps {
    token: string;
}

export function InviteAccept({ token }: InviteAcceptProps) {
    const navigate = useNavigate();
    const { data: invitation, isLoading, error } = useInvitation(token);
    const { mutate: acceptInvitation, isPending: isAccepting } = useAcceptInvitation();

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gray-50">
                <p>Loading invitation...</p>
            </div>
        );
    }

    if (error || !invitation) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
                <Card className="w-full max-w-md">
                    <CardHeader>
                        <CardTitle className="text-red-600">Invalid Invitation</CardTitle>
                        <CardDescription>
                            This invitation link is invalid or has expired.
                        </CardDescription>
                    </CardHeader>
                    <CardFooter>
                        <Button onClick={() => navigate({ to: "/" })} variant="outline" className="w-full">
                            Go Home
                        </Button>
                    </CardFooter>
                </Card>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle>You've been invited!</CardTitle>
                    <CardDescription>
                        You have been invited to join <strong>{invitation.organization_id}</strong> as a{" "}
                        <strong>{invitation.role}</strong>.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2 text-sm text-gray-600">
                        <p>Email: {invitation.email}</p>
                        <p>Organization ID: {invitation.organization_id}</p>
                        {/* Note: In a real app we'd fetch the Org Name, but the ID is sufficient for MVP/Verification */}
                    </div>
                </CardContent>
                <CardFooter className="flex flex-col gap-2">
                    <Button
                        className="w-full"
                        onClick={() => acceptInvitation(token)}
                        disabled={isAccepting}
                    >
                        {isAccepting ? "Joining..." : "Accept Invitation"}
                    </Button>
                    <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => navigate({ to: "/dashboard" })}
                    >
                        Decline
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
