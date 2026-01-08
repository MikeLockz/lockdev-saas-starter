import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Activity,
  ClipboardList,
  FileText,
  Settings,
  Shield,
  Stethoscope,
  Users,
} from "lucide-react";
import { RoleGuard } from "@/components/auth/RoleGuard";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCurrentOrg } from "@/hooks/useCurrentOrg";
import { useOrgMembers } from "@/hooks/useOrgMembers";

export const Route = createFileRoute("/_auth/admin/")({
  component: AdminDashboardPage,
});

function AdminDashboardPage() {
  const { orgId, organization, isLoading: isOrgLoading } = useCurrentOrg();
  const { data: members, isLoading: isMembersLoading } = useOrgMembers(orgId);

  const isLoading = isOrgLoading || isMembersLoading;

  const quickLinks = [
    {
      title: "Team Members",
      description: "Manage organization members",
      href: "/admin/members",
      icon: Users,
    },
    {
      title: "Staff",
      description: "Manage staff accounts",
      href: "/admin/staff",
      icon: ClipboardList,
    },
    {
      title: "Providers",
      description: "Manage healthcare providers",
      href: "/admin/providers",
      icon: Stethoscope,
    },
    {
      title: "Audit Logs",
      description: "View security & activity logs",
      href: "/admin/audit-logs",
      icon: FileText,
    },
    {
      title: "Billing",
      description: "Manage billing & subscription",
      href: "/admin/billing",
      icon: Settings,
    },
  ];

  // Calculate some basic metrics
  const totalMembers = members?.length || 0;
  const adminCount = members?.filter((m) => m.role === "admin").length || 0;
  const staffCount = members?.filter((m) => m.role === "staff").length || 0;

  return (
    <RoleGuard allowedRoles={["admin", "super_admin"]}>
      <Header fixed>
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          <h1 className="text-lg font-semibold">Admin Dashboard</h1>
        </div>
      </Header>
      <Main>
        <div className="space-y-6">
          {/* Org Health Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Organization Health
              </CardTitle>
              <CardDescription>
                {isLoading ? (
                  <Skeleton className="h-4 w-48" />
                ) : (
                  <>Overview of {organization?.name || "your organization"}</>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Total Members</p>
                  {isLoading ? (
                    <Skeleton className="h-8 w-12 mt-1" />
                  ) : (
                    <p className="text-2xl font-bold">{totalMembers}</p>
                  )}
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Admins</p>
                  {isLoading ? (
                    <Skeleton className="h-8 w-12 mt-1" />
                  ) : (
                    <p className="text-2xl font-bold">{adminCount}</p>
                  )}
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Staff</p>
                  {isLoading ? (
                    <Skeleton className="h-8 w-12 mt-1" />
                  ) : (
                    <p className="text-2xl font-bold">{staffCount}</p>
                  )}
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Status</p>
                  <p className="text-2xl font-bold text-green-600">Active</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Links */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Quick Links</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {quickLinks.map((link) => (
                <Link key={link.href} to={link.href}>
                  <Card className="h-full hover:border-primary/50 hover:shadow-md transition-all cursor-pointer">
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          <link.icon className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-base">
                            {link.title}
                          </CardTitle>
                          <CardDescription className="text-sm">
                            {link.description}
                          </CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest member activity in your organization
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center gap-3">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div className="space-y-1">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : members && members.length > 0 ? (
                <div className="space-y-3">
                  {members.slice(0, 5).map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-3 bg-muted/30 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <span className="font-medium text-primary">
                            {(member.display_name || member.email)
                              .charAt(0)
                              .toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium">
                            {member.display_name || "Unknown"}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {member.email}
                          </p>
                        </div>
                      </div>
                      <span className="text-xs bg-muted px-2 py-1 rounded capitalize">
                        {member.role}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">
                  No members found
                </p>
              )}
              {members && members.length > 5 && (
                <div className="mt-4 text-center">
                  <Button asChild variant="outline">
                    <Link to="/admin/members">View All Members</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </Main>
    </RoleGuard>
  );
}
