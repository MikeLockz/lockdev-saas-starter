import { useState } from 'react';
import { formatDateTime } from '@/lib/timezone';
import { useTimezoneContext } from '@/contexts/TimezoneContext';
import { useForm } from 'react-hook-form';
import { Phone, Clock, ArrowUpRight, ArrowDownLeft, User as UserIcon } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useCalls, useCreateCall, useUpdateCall, type Call } from '@/hooks/api/useCalls';
import { usePatients, type PatientListItem } from '@/hooks/api/usePatients';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export function CallLogForm({ activeCall, onClose }: { activeCall?: Call; onClose?: () => void }) {
    const createCall = useCreateCall();
    const updateCall = useUpdateCall();
    const { data: patientsData } = usePatients();
    const patients = patientsData?.items || [];

    const { register, handleSubmit, setValue, formState: { errors } } = useForm({
        defaultValues: {
            direction: activeCall?.direction || 'OUTBOUND',
            phone_number: activeCall?.phone_number || '',
            patient_id: activeCall?.patient_id || '',
            notes: activeCall?.notes || '',
            outcome: activeCall?.outcome || '',
            status: activeCall?.status || 'IN_PROGRESS'
        }
    });

    const onSubmit = (data: any) => {
        if (activeCall) {
            updateCall.mutate({
                id: activeCall.id,
                data: {
                    status: data.status,
                    notes: data.notes,
                    outcome: data.outcome
                }
            }, {
                onSuccess: () => onClose?.()
            });
        } else {
            createCall.mutate(data, {
                onSuccess: () => onClose?.()
            });
        }
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <Label>Direction</Label>
                    <Select
                        defaultValue={activeCall?.direction || 'OUTBOUND'}
                        onValueChange={(val) => setValue('direction', val as 'INBOUND' | 'OUTBOUND')}
                        disabled={!!activeCall}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Select direction" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="INBOUND">Inbound</SelectItem>
                            <SelectItem value="OUTBOUND">Outbound</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div className="space-y-2">
                    <Label>Status</Label>
                    <Select
                        defaultValue={activeCall?.status || 'IN_PROGRESS'}
                        onValueChange={(val) => setValue('status', val as 'QUEUED' | 'IN_PROGRESS' | 'COMPLETED' | 'MISSED')}
                    >
                        <SelectTrigger>
                            <SelectValue placeholder="Call Status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="QUEUED">Queued</SelectItem>
                            <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                            <SelectItem value="COMPLETED">Completed</SelectItem>
                            <SelectItem value="MISSED">Missed</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div className="space-y-2">
                <Label>Patient (Optional)</Label>
                <Select
                    defaultValue={activeCall?.patient_id}
                    onValueChange={(val) => setValue('patient_id', val === 'none' ? '' : val)}
                    disabled={!!activeCall}
                >
                    <SelectTrigger>
                        <SelectValue placeholder="Select patient" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        {patients.map((p: PatientListItem) => (
                            <SelectItem key={p.id} value={p.id}>{p.first_name} {p.last_name}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <div className="space-y-2">
                <Label>Phone Number</Label>
                <Input
                    {...register('phone_number', { required: true })}
                    placeholder="+1234567890"
                    disabled={!!activeCall}
                />
                {errors.phone_number && <span className="text-sm text-red-500">Required</span>}
            </div>

            <div className="space-y-2">
                <Label>Notes</Label>
                <Textarea
                    {...register('notes')}
                    placeholder="Call notes..."
                    className="min-h-[100px]"
                />
            </div>

            <div className="space-y-2">
                <Label>Outcome</Label>
                <Select
                    defaultValue={activeCall?.outcome}
                    onValueChange={(val) => setValue('outcome', val)}
                >
                    <SelectTrigger>
                        <SelectValue placeholder="Select outcome" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="RESOLVED">Resolved</SelectItem>
                        <SelectItem value="CALLBACK_SCHEDULED">Callback Scheduled</SelectItem>
                        <SelectItem value="TRANSFERRED">Transferred</SelectItem>
                        <SelectItem value="VOICEMAIL">Voicemail</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
                <Button type="submit">Save Call</Button>
            </div>
        </form>
    );
}

export function CallCard({ call, onClick }: { call: Call; onClick: () => void }) {
    const timezone = useTimezoneContext();
    return (
        <div
            onClick={onClick}
            className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
        >
            <div className="flex items-center space-x-4">
                <div className={`p-2 rounded-full ${call.direction === 'INBOUND' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'}`}>
                    {call.direction === 'INBOUND' ? <ArrowDownLeft size={16} /> : <ArrowUpRight size={16} />}
                </div>
                <div>
                    <div className="font-medium">{call.patient_name || call.phone_number}</div>
                    <div className="text-sm text-muted-foreground flex items-center space-x-2">
                        <span>{formatDateTime(new Date(call.started_at || call.created_at), 'MMM d, h:mm a', timezone)}</span>
                        {call.duration_seconds && (
                            <>
                                <span>•</span>
                                <span>{Math.floor(call.duration_seconds / 60)}m {call.duration_seconds % 60}s</span>
                            </>
                        )}
                    </div>
                </div>
            </div>
            <div>
                <Badge variant={call.status === 'COMPLETED' ? 'secondary' : call.status === 'IN_PROGRESS' ? 'default' : 'outline'}>
                    {call.status}
                </Badge>
            </div>
        </div>
    );
}

export function CallQueue() {
    const { data: calls } = useCalls({ status: 'QUEUED' });

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-lg flex items-center space-x-2">
                    <Phone className="h-4 w-4" />
                    <span>Call Queue</span>
                    {calls?.length ? <Badge>{calls.length}</Badge> : null}
                </CardTitle>
            </CardHeader>
            <CardContent>
                {calls?.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">No calls in queue</div>
                ) : (
                    <div className="space-y-2">
                        {calls?.map((call: Call) => (
                            <CallCard key={call.id} call={call} onClick={() => { }} />
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

export function CallCenterDashboard() {
    const { data: calls } = useCalls(); // All calls for history
    const [selectedCall, setSelectedCall] = useState<Call | null>(null);
    const [isLogOpen, setIsLogOpen] = useState(false);

    const activeCalls = calls?.filter((c: Call) => c.status === 'IN_PROGRESS') || [];
    const historyCalls = calls?.filter((c: Call) => c.status !== 'IN_PROGRESS' && c.status !== 'QUEUED') || [];

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[calc(100vh-100px)]">
            {/* Left Column: Queue & Active */}
            <div className="space-y-6 flex flex-col h-full">
                <div className="flex justify-between items-center">
                    <h2 className="text-2xl font-bold tracking-tight">Call Center</h2>
                    <Dialog open={isLogOpen} onOpenChange={setIsLogOpen}>
                        <DialogTrigger asChild>
                            <Button onClick={() => setSelectedCall(null)}>
                                <Phone className="mr-2 h-4 w-4" /> Log Call
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>{selectedCall ? 'Edit Call Details' : 'Log New Call'}</DialogTitle>
                            </DialogHeader>
                            <CallLogForm activeCall={selectedCall || undefined} onClose={() => setIsLogOpen(false)} />
                        </DialogContent>
                    </Dialog>
                </div>

                <CallQueue />

                <Card className="flex-1 flex flex-col">
                    <CardHeader>
                        <CardTitle className="text-lg flex items-center space-x-2">
                            <Clock className="h-4 w-4" />
                            <span>Active Calls</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-auto">
                        <div className="space-y-2">
                            {activeCalls.map((call: Call) => (
                                <CallCard
                                    key={call.id}
                                    call={call}
                                    onClick={() => {
                                        setSelectedCall(call);
                                        setIsLogOpen(true);
                                    }}
                                />
                            ))}
                            {activeCalls.length === 0 && (
                                <div className="text-center py-8 text-muted-foreground">No active calls</div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Right Column: History */}
            <div className="md:col-span-2 h-full flex flex-col">
                <Card className="h-full flex flex-col">
                    <CardHeader>
                        <CardTitle>Recent History</CardTitle>
                        <CardDescription>All your organization's call logs</CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-hidden p-0">
                        <ScrollArea className="h-full px-6 pb-6">
                            <div className="divide-y">
                                {historyCalls.map((call: Call) => (
                                    <div
                                        key={call.id}
                                        className="py-4 hover:bg-muted/30 cursor-pointer px-2 rounded -mx-2"
                                        onClick={() => {
                                            setSelectedCall(call);
                                            setIsLogOpen(true);
                                        }}
                                    >
                                        <div className="flex justify-between items-start">
                                            <div className="flex items-start space-x-3">
                                                <Avatar className="h-9 w-9">
                                                    <AvatarFallback><UserIcon className="h-4 w-4" /></AvatarFallback>
                                                </Avatar>
                                                <div>
                                                    <div className="font-medium">{call.patient_name || call.phone_number}</div>
                                                    <div className="text-sm text-muted-foreground">
                                                        Agent: {call.agent_name || 'System'}
                                                    </div>
                                                    {call.notes && (
                                                        <div className="text-sm mt-1 line-clamp-2 text-muted-foreground/80 bg-muted p-1 rounded">
                                                            {call.notes}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <Badge variant="outline" className="mb-1">{call.outcome || 'No outcome'}</Badge>
                                                <div className="text-xs text-muted-foreground">
                                                    {formatDateTime(new Date(call.created_at), 'h:mm a', useTimezoneContext())}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
