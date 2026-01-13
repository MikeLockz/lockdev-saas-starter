import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { useAssignBillingManager, useRemoveBillingManager } from '@/hooks/api/usePatientBilling';
import { usePatientProxies } from '@/hooks/api/useProxies';
import { toast } from 'sonner';
import { User, UserMinus } from 'lucide-react';

interface Props {
    patientId: string;
    currentBillingManagerId?: string | null;
}

export function BillingManagerAssignment({ patientId, currentBillingManagerId }: Props) {
    const { data: proxies } = usePatientProxies(patientId);
    const assignMutation = useAssignBillingManager(patientId);
    const removeMutation = useRemoveBillingManager(patientId);
    const [selectedProxyId, setSelectedProxyId] = useState<string | undefined>(currentBillingManagerId || undefined);

    const activeProxies = proxies?.filter(p => p.status === 'ACTIVE') || [];
    const currentManager = activeProxies.find(p => p.proxy_user_id === currentBillingManagerId);

    const handleAssign = async () => {
        if (!selectedProxyId) return;

        try {
            await assignMutation.mutateAsync(selectedProxyId);
            toast.success('Billing manager assigned successfully');
        } catch (error) {
            toast.error('Failed to assign billing manager');
        }
    };

    const handleRemove = async () => {
        try {
            await removeMutation.mutateAsync();
            setSelectedProxyId(undefined);
            toast.success('Billing manager removed successfully');
        } catch (error) {
            toast.error('Failed to remove billing manager');
        }
    };

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    <CardTitle>Billing Manager</CardTitle>
                </div>
                <CardDescription>
                    Assign a proxy to manage billing on your behalf. They will receive all billing emails and can manage your subscription.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {currentManager ? (
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                            <div>
                                <p className="font-medium">{currentManager.proxy_name}</p>
                                <p className="text-sm text-muted-foreground">{currentManager.proxy_email}</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Currently managing your billing
                                </p>
                            </div>
                            <AlertDialog>
                                <AlertDialogTrigger asChild>
                                    <Button variant="outline" size="sm">
                                        <UserMinus className="h-4 w-4 mr-2" />
                                        Remove
                                    </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                    <AlertDialogHeader>
                                        <AlertDialogTitle>Remove Billing Manager?</AlertDialogTitle>
                                        <AlertDialogDescription>
                                            {currentManager.proxy_name} will no longer be able to manage your billing.
                                            You will receive all billing emails directly. You can reassign them later if needed.
                                        </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                                        <AlertDialogAction onClick={handleRemove}>
                                            Remove Billing Manager
                                        </AlertDialogAction>
                                    </AlertDialogFooter>
                                </AlertDialogContent>
                            </AlertDialog>
                        </div>
                    </div>
                ) : activeProxies.length > 0 ? (
                    <div className="space-y-4">
                        <div>
                            <label className="text-sm font-medium mb-2 block">
                                Select a proxy to manage your billing
                            </label>
                            <Select value={selectedProxyId} onValueChange={setSelectedProxyId}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Choose a proxy..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {activeProxies.map((proxy) => (
                                        <SelectItem key={proxy.proxy_user_id} value={proxy.proxy_user_id}>
                                            {proxy.proxy_name} ({proxy.proxy_email})
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <Button
                            onClick={handleAssign}
                            disabled={!selectedProxyId || assignMutation.isPending}
                        >
                            Assign Billing Manager
                        </Button>
                    </div>
                ) : (
                    <div className="text-center py-4">
                        <p className="text-muted-foreground text-sm">
                            You don't have any active proxies. Add a proxy first to assign them as billing manager.
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
