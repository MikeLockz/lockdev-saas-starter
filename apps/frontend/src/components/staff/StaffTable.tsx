import { useState } from 'react'
import {
    useStaff,
    useDeleteStaff,
    type StaffListItem
} from '@/hooks/useStaff'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Search, Plus, Trash2, Edit2 } from 'lucide-react'
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface StaffTableProps {
    onEdit?: (staff: StaffListItem) => void
    onCreate?: () => void
}

export function StaffTable({ onEdit, onCreate }: StaffTableProps) {
    const [searchDept, setSearchDept] = useState('')
    const [deleteId, setDeleteId] = useState<string | null>(null)

    // Hooks
    const { data, isLoading } = useStaff({
        department: searchDept || undefined
    })
    const deleteStaff = useDeleteStaff()

    // Handlers
    const handleDelete = async () => {
        if (deleteId) {
            await deleteStaff.mutateAsync(deleteId)
            setDeleteId(null)
        }
    }

    return (
        <div className="space-y-4">
            {/* Header Actions */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Filter by department..."
                        value={searchDept}
                        onChange={(e) => setSearchDept(e.target.value)}
                        className="pl-9"
                    />
                </div>
                <Button onClick={onCreate}>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Staff
                </Button>
            </div>

            {/* Table */}
            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Job Title</TableHead>
                            <TableHead>Department</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            Array.from({ length: 5 }).map((_, i) => (
                                <TableRow key={i}>
                                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-8 ml-auto" /></TableCell>
                                </TableRow>
                            ))
                        ) : data?.items.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                    No staff found
                                </TableCell>
                            </TableRow>
                        ) : (
                            data?.items.map((staff) => (
                                <TableRow key={staff.id}>
                                    <TableCell className="font-medium">
                                        {staff.user_display_name || staff.user_email}
                                    </TableCell>
                                    <TableCell>{staff.job_title || '—'}</TableCell>
                                    <TableCell>{staff.department || '—'}</TableCell>
                                    <TableCell>
                                        <Badge variant={staff.is_active ? 'default' : 'secondary'}>
                                            {staff.is_active ? 'Active' : 'Inactive'}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <div className="flex justify-end gap-2">
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => onEdit?.(staff)}
                                            >
                                                <Edit2 className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="text-destructive"
                                                onClick={() => setDeleteId(staff.id)}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Delete Confirmation */}
            <AlertDialog open={!!deleteId} onOpenChange={(open) => !open && setDeleteId(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will remove the staff profile. The user account will remain active.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            onClick={handleDelete}
                        >
                            Delete
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    )
}
