import { Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useCreateCheckout } from "@/hooks/api/useBilling";
import { cn } from "@/lib/utils";

interface Plan {
  id: string;
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  popular?: boolean;
  priceId: string;
}

const plans: Plan[] = [
  {
    id: "starter",
    name: "Starter",
    price: "$29",
    period: "/month",
    description: "Perfect for small practices",
    features: [
      "Up to 100 patients",
      "Basic scheduling",
      "Document storage (5GB)",
      "Email support",
    ],
    priceId: "price_starter",
  },
  {
    id: "professional",
    name: "Professional",
    price: "$79",
    period: "/month",
    description: "For growing healthcare providers",
    features: [
      "Up to 500 patients",
      "Advanced scheduling",
      "Document storage (25GB)",
      "Priority support",
      "Care team management",
      "Proxy access",
    ],
    popular: true,
    priceId: "price_professional",
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "$199",
    period: "/month",
    description: "For large organizations",
    features: [
      "Unlimited patients",
      "Full scheduling suite",
      "Document storage (100GB)",
      "24/7 phone support",
      "Advanced analytics",
      "Custom integrations",
      "Dedicated account manager",
    ],
    priceId: "price_enterprise",
  },
];

interface PlanSelectorProps {
  currentPlanId?: string | null;
}

export function PlanSelector({ currentPlanId }: PlanSelectorProps) {
  const createCheckout = useCreateCheckout();

  const handleSelectPlan = (priceId: string) => {
    createCheckout.mutate({ price_id: priceId });
  };

  return (
    <div className="grid gap-6 md:grid-cols-3">
      {plans.map((plan) => {
        const isCurrentPlan = currentPlanId === plan.priceId;
        return (
          <Card
            key={plan.id}
            className={cn(
              "relative flex flex-col",
              plan.popular && "border-primary shadow-lg",
            )}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
                  Most Popular
                </span>
              </div>
            )}
            <CardHeader className="text-center">
              <CardTitle className="text-xl">{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
              <div className="mt-4">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-muted-foreground">{plan.period}</span>
              </div>
            </CardHeader>
            <CardContent className="flex-1">
              <ul className="space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button
                className="w-full"
                variant={plan.popular ? "default" : "outline"}
                disabled={createCheckout.isPending || isCurrentPlan}
                onClick={() => handleSelectPlan(plan.priceId)}
              >
                {createCheckout.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : isCurrentPlan ? (
                  "Current Plan"
                ) : (
                  "Get Started"
                )}
              </Button>
            </CardFooter>
          </Card>
        );
      })}
    </div>
  );
}
