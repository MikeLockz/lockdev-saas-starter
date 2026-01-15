import {
  AlertCircle,
  Calculator,
  DollarSign,
  TrendingDown,
  TrendingUp,
  Users,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useBillingAnalytics } from "@/hooks/api/useAdminBilling";
import { formatCurrency } from "@/lib/utils";

export function BillingAnalyticsCards() {
  const { data: analytics, isLoading } = useBillingAnalytics();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-5 w-5" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!analytics) return null;

  const cards = [
    {
      title: "Total MRR",
      value: formatCurrency(analytics.total_mrr_cents / 100),
      icon: DollarSign,
      color: "text-green-600",
      bgColor: "bg-green-50 dark:bg-green-900/20",
    },
    {
      title: "Active Subscriptions",
      value: analytics.total_active_subscriptions.toString(),
      icon: Users,
      color: "text-blue-600",
      bgColor: "bg-blue-50 dark:bg-blue-900/20",
    },
    {
      title: "New This Month",
      value: analytics.new_subscriptions_this_month.toString(),
      icon: TrendingUp,
      color: "text-emerald-600",
      bgColor: "bg-emerald-50 dark:bg-emerald-900/20",
    },
    {
      title: "Churn Rate",
      value: `${(analytics.churn_rate * 100).toFixed(1)}%`,
      icon: TrendingDown,
      color: "text-red-600",
      bgColor: "bg-red-50 dark:bg-red-900/20",
    },
    {
      title: "ARPU",
      value: formatCurrency(analytics.average_revenue_per_user_cents / 100),
      icon: Calculator,
      color: "text-purple-600",
      bgColor: "bg-purple-50 dark:bg-purple-900/20",
    },
    {
      title: "Failed Payments",
      value: analytics.failed_payments_this_month.toString(),
      icon: AlertCircle,
      color:
        analytics.failed_payments_this_month > 0
          ? "text-orange-600"
          : "text-gray-400",
      bgColor:
        analytics.failed_payments_this_month > 0
          ? "bg-orange-50 dark:bg-orange-900/20"
          : "bg-gray-50 dark:bg-gray-900/20",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cards.map((card) => (
        <Card key={card.title} className="overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <div className={`p-2 rounded-full ${card.bgColor}`}>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
