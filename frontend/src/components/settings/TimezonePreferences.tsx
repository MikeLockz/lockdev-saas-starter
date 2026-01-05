/**
 * TimezonePreferences component for user settings.
 * Allows users to set/clear their timezone preference.
 */
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TimezoneSelector } from './TimezoneSelector';
import { useTimezoneWithSource } from '@/hooks/useTimezone';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Loader2, RotateCcw } from 'lucide-react';

export function TimezonePreferences() {
    const queryClient = useQueryClient();
    const { data: tzData, isLoading } = useTimezoneWithSource();
    const [selectedTz, setSelectedTz] = useState<string | null>(null);

    const updateMutation = useMutation({
        mutationFn: async (timezone: string) => {
            const response = await api.patch('/api/v1/users/me/timezone', { timezone });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['userTimezone'] });
            queryClient.invalidateQueries({ queryKey: ['currentUser'] });
            toast.success('Timezone updated');
            setSelectedTz(null);
        },
        onError: () => {
            toast.error('Failed to update timezone');
        },
    });

    const clearMutation = useMutation({
        mutationFn: async () => {
            const response = await api.delete('/api/v1/users/me/timezone');
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['userTimezone'] });
            queryClient.invalidateQueries({ queryKey: ['currentUser'] });
            toast.success('Timezone preference cleared');
        },
        onError: () => {
            toast.error('Failed to clear timezone');
        },
    });

    const currentTz = tzData?.timezone || 'America/New_York';
    const source = tzData?.source || 'organization';
    const isPersonal = source === 'user';

    const handleSave = () => {
        if (selectedTz) {
            updateMutation.mutate(selectedTz);
        }
    };

    const handleClear = () => {
        clearMutation.mutate();
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Timezone</CardTitle>
                <CardDescription>
                    Set your preferred timezone for dates and times. If not set, your organization's timezone is used.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                    <Badge variant={isPersonal ? 'default' : 'secondary'}>
                        {isPersonal ? 'Personal preference' : 'Organization default'}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                        Currently: {currentTz}
                    </span>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                    <div className="flex-1">
                        <TimezoneSelector
                            value={selectedTz || currentTz}
                            onChange={setSelectedTz}
                            disabled={isLoading || updateMutation.isPending}
                        />
                    </div>
                    <div className="flex gap-2">
                        <Button
                            onClick={handleSave}
                            disabled={!selectedTz || selectedTz === currentTz || updateMutation.isPending}
                        >
                            {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Save
                        </Button>
                        {isPersonal && (
                            <Button
                                variant="outline"
                                onClick={handleClear}
                                disabled={clearMutation.isPending}
                            >
                                {clearMutation.isPending ? (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                ) : (
                                    <RotateCcw className="mr-2 h-4 w-4" />
                                )}
                                Use Org Default
                            </Button>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
