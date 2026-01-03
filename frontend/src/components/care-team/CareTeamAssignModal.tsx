import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { useProviders } from '@/hooks/useProviders'
import { useAssignToCareTeam } from '@/hooks/useCareTeam'

const assignSchema = z.object({
    provider_id: z.string().uuid("Please select a provider"),
    role: z.enum(["PRIMARY", "SPECIALIST", "CONSULTANT"]),
})

type FormData = z.infer<typeof assignSchema>

interface CareTeamAssignModalProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    patientId: string
}

export function CareTeamAssignModal({ open, onOpenChange, patientId }: CareTeamAssignModalProps) {
    const { data: providers } = useProviders({ isActive: true })
    const assignProvider = useAssignToCareTeam()
    const [error, setError] = useState<string | null>(null)

    const form = useForm<FormData>({
        resolver: zodResolver(assignSchema),
        defaultValues: {
            provider_id: '',
            role: 'SPECIALIST',
        },
    })

    const onSubmit = async (data: FormData) => {
        try {
            setError(null)
            await assignProvider.mutateAsync({
                patientId,
                data: {
                    provider_id: data.provider_id,
                    role: data.role,
                }
            })
            form.reset()
            onOpenChange(false)
        } catch (err: any) {
            console.error(err)
            const msg = err.response?.data?.detail || "Failed to assign provider"
            setError(msg)
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Assign Care Team Member</DialogTitle>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
                            name="provider_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Provider</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select a provider" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            {providers?.items.map((provider) => (
                                                <SelectItem key={provider.id} value={provider.id}>
                                                    {provider.user_display_name || provider.user_email}
                                                    {provider.specialty ? ` — ${provider.specialty}` : ''}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="role"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Role</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select a role" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            <SelectItem value="PRIMARY">Primary Care Provider</SelectItem>
                                            <SelectItem value="SPECIALIST">Specialist</SelectItem>
                                            <SelectItem value="CONSULTANT">Consultant</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {error && (
                            <div className="text-sm font-medium text-destructive">
                                {error}
                            </div>
                        )}

                        <DialogFooter>
                            <Button type="submit" disabled={assignProvider.isPending}>
                                Assign Provider
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
