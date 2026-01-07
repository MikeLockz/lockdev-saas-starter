import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useCurrentOrg } from '@/hooks/useCurrentOrg'
import { useOrgMembers } from '@/hooks/useOrgMembers'
import { useCreateStaff, useUpdateStaff, type StaffListItem } from '@/hooks/useStaff'
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
const staffSchema = z.object({
    user_id: z.string().uuid("Please select a user"),
    job_title: z.string().optional(),
    department: z.string().optional(),
    employee_id: z.string().optional(),
})

type FormData = z.infer<typeof staffSchema>

interface StaffFormProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    staff?: StaffListItem | null
}

export function StaffForm({ open, onOpenChange, staff }: StaffFormProps) {
    const { orgId } = useCurrentOrg()
    const { data: members } = useOrgMembers(orgId)
    const createStaff = useCreateStaff()
    const updateStaff = useUpdateStaff()
    const [error, setError] = useState<string | null>(null)

    const form = useForm<FormData>({
        resolver: zodResolver(staffSchema),
        defaultValues: {
            user_id: '',
            job_title: '',
            department: '',
            employee_id: '',
        },
    })

    useEffect(() => {
        if (open) {
            form.reset({
                user_id: staff?.user_id || '',
                job_title: staff?.job_title || '',
                department: staff?.department || '',
                employee_id: '', // Not in list view, would need fetch details
            })
            setError(null)
        }
    }, [open, staff, form])

    const onSubmit = async (data: FormData) => {
        try {
            setError(null)
            const payload = {
                ...data,
                job_title: data.job_title || undefined,
                department: data.department || undefined,
                employee_id: data.employee_id || undefined,
            }

            if (staff) {
                await updateStaff.mutateAsync({
                    staffId: staff.id,
                    data: payload
                })
            } else {
                await createStaff.mutateAsync(payload)
            }
            onOpenChange(false)
        } catch (err: any) {
            console.error(err)
            const msg = err.response?.data?.detail || "Failed to save staff member"
            setError(msg)
        }
    }

    const isEditing = !!staff

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{isEditing ? 'Edit Staff Application' : 'Add Staff Member'}</DialogTitle>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
                                                <SelectValue placeholder="Select a user" />
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
                            name="job_title"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Job Title</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Nurse Practitioner" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="department"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Department</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Cardiology" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="employee_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Employee ID</FormLabel>
                                    <FormControl>
                                        <Input placeholder="EMP-001" {...field} />
                                    </FormControl>
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
                            <Button type="submit" disabled={createStaff.isPending || updateStaff.isPending}>
                                {isEditing ? 'Save Changes' : 'Create Member'}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
