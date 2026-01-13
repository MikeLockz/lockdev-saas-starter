import { createFileRoute } from '@tanstack/react-router';
import { PatientSubscriptionCard } from '@/components/billing/PatientSubscriptionCard';
import { PatientPlanSelector } from '@/components/billing/PatientPlanSelector';
import { TransactionHistory } from '@/components/billing/TransactionHistory';
import { BillingManagerAssignment } from '@/components/billing/BillingManagerAssignment';
import { usePatientSubscription } from '@/hooks/api/usePatientBilling';
import { useCurrentPatient } from '@/hooks/useCurrentPatient';

export const Route = createFileRoute('/_auth/patient/billing')({
    component: PatientBillingPage,
});

function PatientBillingPage() {
    const { currentPatient } = useCurrentPatient();
    const { data: subscription, isLoading } = usePatientSubscription(currentPatient?.id || '');

    if (isLoading) {
        return <div>Loading billing information...</div>;
    }

    const hasActiveSubscription = subscription?.status === 'ACTIVE' || subscription?.status === 'TRIALING';

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <h1 className="text-3xl font-bold mb-6">My Billing</h1>

            {/* Current Subscription Status */}
            <div className="mb-8">
                <PatientSubscriptionCard
                    subscription={subscription}
                    patientId={currentPatient?.id || ''}
                />
            </div>

            {/* Billing Manager Assignment (if has proxies) */}
            <div className="mb-8">
                <BillingManagerAssignment
                    patientId={currentPatient?.id || ''}
                    currentBillingManagerId={subscription?.billing_manager_id}
                />
            </div>

            {/* Plan Selection (if no subscription) */}
            {!hasActiveSubscription && (
                <div className="mb-8">
                    <h2 className="text-2xl font-semibold mb-4">Choose a Plan</h2>
                    <PatientPlanSelector patientId={currentPatient?.id || ''} />
                </div>
            )}

            {/* Transaction History */}
            {hasActiveSubscription && (
                <div>
                    <h2 className="text-2xl font-semibold mb-4">Payment History</h2>
                    <TransactionHistory patientId={currentPatient?.id || ''} />
                </div>
            )}
        </div>
    );
}
