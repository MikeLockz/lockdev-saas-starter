import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check } from 'lucide-react';
import { usePatientCheckout } from '@/hooks/api/usePatientBilling';

const PLANS = [
    {
        id: 'price_starter',
        name: 'Starter',
        price: 29,
        features: [
            'Basic scheduling',
            'Email reminders',
            '5GB document storage',
            'Email support',
        ],
    },
    {
        id: 'price_professional',
        name: 'Professional',
        price: 79,
        popular: true,
        features: [
            'Everything in Starter',
            'Advanced scheduling',
            '25GB document storage',
            'Priority support',
            'Care team access',
        ],
    },
    {
        id: 'price_enterprise',
        name: 'Enterprise',
        price: 199,
        features: [
            'Everything in Professional',
            'Unlimited storage',
            '24/7 phone support',
            'Custom integrations',
            'Dedicated account manager',
        ],
    },
];

interface Props {
    patientId: string;
}

export function PatientPlanSelector({ patientId }: Props) {
    const checkoutMutation = usePatientCheckout(patientId);

    return (
        <div className="grid md:grid-cols-3 gap-6">
            {PLANS.map((plan) => (
                <Card
                    key={plan.id}
                    className={plan.popular ? 'border-primary shadow-lg' : ''}
                >
                    <CardHeader>
                        {plan.popular && (
                            <Badge className="w-fit mb-2">Most Popular</Badge>
                        )}
                        <CardTitle>{plan.name}</CardTitle>
                        <CardDescription>
                            <span className="text-3xl font-bold text-foreground">
                                ${plan.price}
                            </span>
                            /month
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <ul className="space-y-2">
                            {plan.features.map((feature, idx) => (
                                <li key={idx} className="flex items-center gap-2">
                                    <Check className="h-4 w-4 text-primary" />
                                    <span className="text-sm">{feature}</span>
                                </li>
                            ))}
                        </ul>
                        <Button
                            className="w-full"
                            onClick={() => checkoutMutation.mutate(plan.id)}
                            disabled={checkoutMutation.isPending}
                        >
                            {checkoutMutation.isPending ? 'Loading...' : 'Get Started'}
                        </Button>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
