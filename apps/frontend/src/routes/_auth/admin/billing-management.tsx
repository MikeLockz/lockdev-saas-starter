import { createFileRoute } from "@tanstack/react-router";
import { BillingAnalyticsCards } from "@/components/admin/billing/BillingAnalyticsCards";
import { BillingManagersList } from "@/components/admin/billing/BillingManagersList";
import { SubscriptionsList } from "@/components/admin/billing/SubscriptionsList";
import { TransactionsList } from "@/components/admin/billing/TransactionsList";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export const Route = createFileRoute("/_auth/admin/billing-management")({
  component: AdminBillingManagementPage,
});

function AdminBillingManagementPage() {
  return (
    <div className="container mx-auto py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Billing Management
        </h1>
        <p className="text-muted-foreground">
          Manage subscriptions, process refunds, and view billing analytics
        </p>
      </div>

      {/* Analytics Cards */}
      <BillingAnalyticsCards />

      {/* Tabs for Subscriptions, Transactions, and Billing Managers */}
      <Tabs defaultValue="subscriptions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="billing-managers">Billing Managers</TabsTrigger>
        </TabsList>

        <TabsContent value="subscriptions">
          <SubscriptionsList />
        </TabsContent>

        <TabsContent value="transactions">
          <TransactionsList />
        </TabsContent>

        <TabsContent value="billing-managers">
          <BillingManagersList />
        </TabsContent>
      </Tabs>
    </div>
  );
}
