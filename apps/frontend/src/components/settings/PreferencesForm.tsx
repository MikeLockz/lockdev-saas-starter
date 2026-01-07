import { usePreferences } from '@/hooks/usePreferences';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';

function Toggle({
    checked,
    onChange,
    disabled,
}: {
    checked: boolean;
    onChange: (checked: boolean) => void;
    disabled?: boolean;
}) {
    return (
        <button
            type="button"
            role="switch"
            aria-checked={checked}
            disabled={disabled}
            onClick={() => onChange(!checked)}
            className={`
        relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent 
        transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
        ${checked ? 'bg-primary' : 'bg-gray-200 dark:bg-gray-700'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
        >
            <span
                className={`
          pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 
          transition duration-200 ease-in-out
          ${checked ? 'translate-x-5' : 'translate-x-0'}
        `}
            />
        </button>
    );
}

export function PreferencesForm() {
    const { preferences, isLoading, updatePreferences } = usePreferences();

    const handleChange = async (field: 'transactional_consent' | 'marketing_consent', value: boolean) => {
        await updatePreferences.mutateAsync({ [field]: value });
    };

    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Communication Preferences</CardTitle>
                    <CardDescription>Control how we contact you</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Communication Preferences</CardTitle>
                <CardDescription>
                    Control how we contact you. Some notifications are required for your care.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="flex items-start justify-between p-4 rounded-lg border">
                    <div className="space-y-1">
                        <Label htmlFor="transactional" className="font-medium">
                            Appointment & Billing Notifications
                        </Label>
                        <p className="text-sm text-muted-foreground">
                            Essential notifications about appointments, billing, and care reminders.
                            Required for HIPAA compliance.
                        </p>
                    </div>
                    <Toggle
                        checked={preferences?.transactional_consent ?? true}
                        onChange={(checked) => handleChange('transactional_consent', checked)}
                        disabled={updatePreferences.isPending}
                    />
                </div>

                <div className="flex items-start justify-between p-4 rounded-lg border">
                    <div className="space-y-1">
                        <Label htmlFor="marketing" className="font-medium">
                            Marketing & Promotional
                        </Label>
                        <p className="text-sm text-muted-foreground">
                            Updates about new services, health tips, and promotions.
                            You can unsubscribe anytime.
                        </p>
                    </div>
                    <Toggle
                        checked={preferences?.marketing_consent ?? false}
                        onChange={(checked) => handleChange('marketing_consent', checked)}
                        disabled={updatePreferences.isPending}
                    />
                </div>

                {preferences?.updated_at && (
                    <p className="text-sm text-muted-foreground">
                        Last updated: {new Date(preferences.updated_at).toLocaleString()}
                    </p>
                )}
            </CardContent>
        </Card>
    );
}
