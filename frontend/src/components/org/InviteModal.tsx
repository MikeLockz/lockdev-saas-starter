
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { useCreateInvitation } from "../../hooks/useCreateInvitation";
import { useCurrentOrg } from "../../hooks/useCurrentOrg";

interface InviteFormData {
    email: string;
    role: string;
}

export function InviteModal() {
    const [open, setOpen] = useState(false);
    const { organization: currentOrg } = useCurrentOrg();
    const { mutate: createInvitation, isPending } = useCreateInvitation(
        currentOrg?.id || ""
    );

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<InviteFormData>({
        defaultValues: {
            email: "",
            role: "STAFF",
        },
    });

    const onSubmit = (data: InviteFormData) => {
        if (!currentOrg) return;

        createInvitation(
            { email: data.email, role: data.role },
            {
                onSuccess: () => {
                    toast.success("Invitation sent successfully");
                    setOpen(false);
                    reset();
                },
                onError: (error) => {
                    toast.error("Failed to send invitation: " + error.message);
                },
            }
        );
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>Invite Member</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Invite Team Member</DialogTitle>
                    <DialogDescription>
                        Send an invitation to join your organization. They will receive an email
                        with instructions.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="email">Email address</Label>
                        <Input
                            id="email"
                            placeholder="colleague@example.com"
                            type="email"
                            {...register("email", {
                                required: "Email is required",
                                pattern: {
                                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                    message: "Invalid email address"
                                }
                            })}
                        />
                        {errors.email && (
                            <p className="text-sm text-red-500">{errors.email.message}</p>
                        )}
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="role">Role</Label>
                        <select
                            id="role"
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            {...register("role")}
                        >
                            <option value="STAFF">Staff</option>
                            <option value="PROVIDER">Provider</option>
                            <option value="ADMIN">Admin</option>
                        </select>
                    </div>
                    <DialogFooter>
                        <Button type="submit" disabled={isPending}>
                            {isPending ? "Sending..." : "Send Invitation"}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
