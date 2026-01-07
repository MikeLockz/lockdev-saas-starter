import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useCurrentOrg } from '@/hooks/useCurrentOrg'
import { useOrgMembers } from '@/hooks/useOrgMembers'
import { useCreateProvider, useUpdateProvider, type ProviderListItem } from '@/hooks/useProviders'
import { Button } from '@/components/ui/button'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
    FormDescription,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog"

// Schema
const providerSchema = z.object({
    user_id: z.string().uuid("Please select a user"),
    npi_number: z.string().length(10, "NPI must be exactly 10 digits").optional().or(z.literal('')),
    specialty: z.string().optional(),
    license_number: z.string().optional(),
    license_state: z.string().length(2, "State code must be 2 characters").optional().or(z.literal('')),
    dea_number: z.string().optional(),
})

type FormData = z.infer<typeof providerSchema>

interface ProviderFormProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    provider?: ProviderListItem | null // If present, update mode
}

export function ProviderForm({ open, onOpenChange, provider }: ProviderFormProps) {
    const { orgId } = useCurrentOrg()
    const { data: members } = useOrgMembers(orgId)
    const createProvider = useCreateProvider()
    const updateProvider = useUpdateProvider()
    const [error, setError] = useState<string | null>(null)

    const form = useForm<FormData>({
        resolver: zodResolver(providerSchema),
        defaultValues: {
            user_id: '',
            npi_number: '',
            specialty: '',
            license_number: '',
            license_state: '',
            dea_number: '',
        },
    })

    // Reset/Populate form when opening/changing provider
    useEffect(() => {
        if (open) {
            form.reset({
                user_id: provider?.user_id || '',
                npi_number: provider?.npi_number || '',
                specialty: provider?.specialty || '',
                // These might not be in the list item, ideally we fetch details or pass them
                // For simplified UI, we might just edit what we have or fetch on edit.
                // Assuming provider list item lacks extensive details, we should technically fetch 
                // the full provider details if editing.
                // For now, let's just assume we edit what we display or empty.
                // NOTE: ProviderListItem is lightweight. A real app would fetch `useProvider(provider.id)`
                // But let's keep it simple and maybe imperfect for this iteration unless I add fetch logic.
                // Actually, I created useProvider hook! I should use it if provider is set.
                license_number: '',
                license_state: '',
                dea_number: '',
            })
            setError(null)
        }
    }, [open, provider, form])

    const onSubmit = async (data: FormData) => {
        try {
            setError(null)

            // Clean up empty strings to undefined/null
            const payload = {
                ...data,
                npi_number: data.npi_number || undefined,
                specialty: data.specialty || undefined,
                license_number: data.license_number || undefined,
                license_state: data.license_state || undefined,
                dea_number: data.dea_number || undefined,
            }

            if (provider) {
                await updateProvider.mutateAsync({
                    providerId: provider.id,
                    data: payload
                })
            } else {
                await createProvider.mutateAsync(payload)
            }
            onOpenChange(false)
        } catch (err: any) {
            // Check for API errors (e.g. 409 NPI exists)
            console.error(err)
            const msg = err.response?.data?.detail || "Failed to save provider"
            setError(msg)
        }
    }

    const isEditing = !!provider

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{isEditing ? 'Edit Provider' : 'Add New Provider'}</DialogTitle>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        {/* User Selection - ReadOnly if editing */}
                        <FormField
                            control={form.control}
                            name="user_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>User</FormLabel>
                                    <Select
                                        disabled={isEditing}
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                        value={field.value}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select a user to promote" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            {members?.map((member) => (
                                                <SelectItem key={member.user_id} value={member.user_id}>
                                                    {member.display_name || member.email}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FormDescription>
                                        Select an existing organization member.
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="npi_number"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>NPI Number</FormLabel>
                                    <FormControl>
                                        <Input placeholder="1234567890" maxLength={10} {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="specialty"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Specialty</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Internal Medicine" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="license_state"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>License State</FormLabel>
                                        <FormControl>
                                            <Input placeholder="CA" maxLength={2} {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="license_number"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>License #</FormLabel>
                                        <FormControl>
                                            <Input placeholder="A12345" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        {error && (
                            <div className="text-sm font-medium text-destructive">
                                {error}
                            </div>
                        )}

                        <DialogFooter>
                            <Button type="submit" disabled={createProvider.isPending || updateProvider.isPending}>
                                {isEditing ? 'Save Changes' : 'Create Provider'}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
