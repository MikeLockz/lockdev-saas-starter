import { useState, useMemo } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useDebounce } from '@/hooks/useDebounce'
import { usePatients, type PatientListItem, type PatientSearchParams } from '@/hooks/api/usePatients'
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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Search, ChevronLeft, ChevronRight, Plus } from 'lucide-react'
import { format } from 'date-fns'

interface PatientTableProps {
    onPatientClick?: (patient: PatientListItem) => void
}

export function PatientTable({ onPatientClick }: PatientTableProps) {
    const navigate = useNavigate()
    const [searchInput, setSearchInput] = useState('')
    const [status, setStatus] = useState<string>('ACTIVE')
    const [page, setPage] = useState(0)
    const pageSize = 20

    const debouncedSearch = useDebounce(searchInput, 300)

    const params: PatientSearchParams = useMemo(() => ({
        name: debouncedSearch || undefined,
        status: status !== 'ALL' ? status : undefined,
        limit: pageSize,
        offset: page * pageSize,
    }), [debouncedSearch, status, page])

    const { data, isLoading, error } = usePatients(params)

    const handleRowClick = (patient: PatientListItem) => {
        if (onPatientClick) {
            onPatientClick(patient)
        } else {
            navigate({ to: `/patients/${patient.id}` })
        }
    }

    const totalPages = data ? Math.ceil(data.total / pageSize) : 0

    if (error) {
        return (
            <div className="p-8 text-center text-destructive">
                Error loading patients: {error.message}
            </div>
        )
    }

    return (
        <div className="space-y-4">
            {/* Search and Filter Bar */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search by name..."
                        value={searchInput}
                        onChange={(e) => {
                            setSearchInput(e.target.value)
                            setPage(0)
                        }}
                        className="pl-9"
                    />
                </div>
                <div className="flex items-center gap-2">
                    <Select value={status} onValueChange={(v: string) => { setStatus(v); setPage(0) }}>
                        <SelectTrigger className="w-[150px]">
                            <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="ACTIVE">Active</SelectItem>
                            <SelectItem value="DISCHARGED">Discharged</SelectItem>
                            <SelectItem value="ALL">All</SelectItem>
                        </SelectContent>
                    </Select>
                    <Button onClick={() => navigate({ to: '/patients/new' })}>
                        <Plus className="mr-2 h-4 w-4" />
                        New Patient
                    </Button>
                </div>
            </div>

            {/* Table */}
            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>DOB</TableHead>
                            <TableHead>MRN</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Enrolled</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            Array.from({ length: 5 }).map((_, i) => (
                                <TableRow key={i}>
                                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                </TableRow>
                            ))
                        ) : data?.items.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                    No patients found
                                </TableCell>
                            </TableRow>
                        ) : (
                            data?.items.map((patient) => (
                                <TableRow
                                    key={patient.id}
                                    className="cursor-pointer hover:bg-muted/50"
                                    onClick={() => handleRowClick(patient)}
                                >
                                    <TableCell className="font-medium">
                                        {patient.last_name}, {patient.first_name}
                                    </TableCell>
                                    <TableCell>
                                        {format(new Date(patient.dob), 'MM/dd/yyyy')}
                                    </TableCell>
                                    <TableCell className="font-mono text-sm">
                                        {patient.medical_record_number || '—'}
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant={patient.status === 'ACTIVE' ? 'default' : 'secondary'}>
                                            {patient.status}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-muted-foreground">
                                        {patient.enrolled_at ? format(new Date(patient.enrolled_at), 'MM/dd/yyyy') : '—'}
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Pagination */}
            {data && data.total > pageSize && (
                <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                        Showing {page * pageSize + 1} to {Math.min((page + 1) * pageSize, data.total)} of {data.total}
                    </div>
                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage((p) => Math.max(0, p - 1))}
                            disabled={page === 0}
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                        <span className="text-sm">
                            Page {page + 1} of {totalPages}
                        </span>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage((p) => p + 1)}
                            disabled={page >= totalPages - 1}
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}
