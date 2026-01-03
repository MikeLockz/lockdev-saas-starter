import { useState } from 'react'
import { useCareTeam, useRemoveFromCareTeam } from '@/hooks/useCareTeam'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Trash2, UserPlus } from 'lucide-react'
import { format } from 'date-fns'
import { CareTeamAssignModal } from './CareTeamAssignModal'
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

interface CareTeamListProps {
    patientId: string
}

export function CareTeamList({ patientId }: CareTeamListProps) {
    const { data, isLoading } = useCareTeam(patientId)
    const removeMember = useRemoveFromCareTeam()
    const [isAssignOpen, setIsAssignOpen] = useState(false)
    const [removeId, setRemoveId] = useState<string | null>(null)

    const handleRemove = async () => {
        if (removeId) {
            await removeMember.mutateAsync({
                patientId,
                assignmentId: removeId
            })
            setRemoveId(null)
        }
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Care Team</h3>
                <Button size="sm" onClick={() => setIsAssignOpen(true)}>
                    <UserPlus className="mr-2 h-4 w-4" />
                    Assign Member
                </Button>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Provider</TableHead>
                            <TableHead>Role</TableHead>
                            <TableHead>Specialty</TableHead>
                            <TableHead>Assigned</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            Array.from({ length: 3 }).map((_, i) => (
                                <TableRow key={i}>
                                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-8 ml-auto" /></TableCell>
                                </TableRow>
                            ))
                        ) : !data || data.members.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center py-6 text-muted-foreground">
                                    No care team members assigned
                                </TableCell>
                            </TableRow>
                        ) : (
                            data.members.map((member) => (
                                <TableRow key={member.assignment_id}>
                                    <TableCell className="font-medium">
                                        {member.provider_name}
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={member.role === 'PRIMARY' ? 'default' : 'outline'}>
                                            {member.role}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>{member.provider_specialty || '—'}</TableCell>
                                    <TableCell>
                                        {format(new Date(member.assigned_at), 'MMM d, yyyy')}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="text-destructive"
                                            onClick={() => setRemoveId(member.assignment_id)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            <CareTeamAssignModal
                open={isAssignOpen}
                onOpenChange={setIsAssignOpen}
                patientId={patientId}
            />

            {/* Remove Confirmation */}
            <AlertDialog open={!!removeId} onOpenChange={(open) => !open && setRemoveId(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Remove from Care Team?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will remove the provider from this patient's care team.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            onClick={handleRemove}
                        >
                            Remove
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    )
}
