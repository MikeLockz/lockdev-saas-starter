import { Link, useRouterState } from "@tanstack/react-router";
import {
  Building2,
  Calendar,
  ClipboardList,
  CreditCard,
  FileText,
  Heart,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  type LucideIcon,
  MessageSquare,
  Phone,
  Settings,
  Shield,
  Users,
} from "lucide-react";
import { useMemo } from "react";
import { OrgSwitcher } from "@/components/org/OrgSwitcher";
import { TimezoneDisplay } from "@/components/settings";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";
import { type UserRole, useUserRole } from "@/hooks/useUserRole";

interface NavItem {
  title: string;
  url: string;
  icon: LucideIcon;
  /** Roles that can see this item. If empty/undefined, all roles can see it. */
  roles?: UserRole[];
}

/**
 * Navigation items organized by section.
 * Each item can optionally specify which roles can see it.
 */
const mainNavItems: NavItem[] = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: LayoutDashboard,
    // All roles see dashboard
  },
  {
    title: "My Appointments",
    url: "/appointments",
    icon: Calendar,
    roles: ["patient", "proxy"],
  },
  {
    title: "Appointments",
    url: "/appointments",
    icon: Calendar,
    roles: ["provider", "staff", "super_admin", "admin", "member"],
  },
  {
    title: "My Care Team",
    url: "/patients", // Links to their own patient profile
    icon: Heart,
    roles: ["patient"],
  },
  {
    title: "My Patients",
    url: "/proxy/patients",
    icon: Users,
    roles: ["proxy"],
  },
  {
    title: "Patients",
    url: "/patients",
    icon: Users,
    roles: ["provider", "staff", "super_admin", "admin"],
  },
  {
    title: "Tasks",
    url: "/tasks",
    icon: ClipboardList,
    roles: ["staff", "super_admin", "admin"],
  },
  {
    title: "Call Center",
    url: "/call-center",
    icon: Phone,
    roles: ["staff", "super_admin", "admin"],
  },
  {
    title: "Messages",
    url: "/messages",
    icon: MessageSquare,
    // All roles see messages
  },
];

const adminNavItems: NavItem[] = [
  {
    title: "Team Members",
    url: "/admin/members",
    icon: Users,
    roles: ["super_admin", "admin"],
  },
  {
    title: "Providers",
    url: "/admin/providers",
    icon: Heart,
    roles: ["super_admin", "admin"],
  },
  {
    title: "Staff",
    url: "/admin/staff",
    icon: ClipboardList,
    roles: ["super_admin", "admin"],
  },
  {
    title: "Audit Logs",
    url: "/admin/audit-logs",
    icon: FileText,
    roles: ["super_admin", "admin"],
  },
];

const superAdminNavItems: NavItem[] = [
  {
    title: "Platform Admin",
    url: "/super-admin",
    icon: Shield,
    roles: ["super_admin"],
  },
  {
    title: "Organizations",
    url: "/super-admin/organizations",
    icon: Building2,
    roles: ["super_admin"],
  },
  {
    title: "Billing Management",
    url: "/admin/billing-management",
    icon: CreditCard,
    roles: ["super_admin"],
  },
];

const bottomNavItems: NavItem[] = [
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
    // All roles see settings
  },
  {
    title: "Help & Support",
    url: "/help",
    icon: HelpCircle,
    // All roles see help
  },
];

/**
 * Filter nav items based on user role.
 * Items with no roles array are shown to everyone.
 */
function filterNavItems(items: NavItem[], role: UserRole): NavItem[] {
  return items.filter((item) => {
    if (!item.roles || item.roles.length === 0) return true;
    return item.roles.includes(role);
  });
}

export function AppSidebar() {
  const { user, signOut } = useAuth();
  const { roleInfo, isLoading } = useUserRole();
  const routerState = useRouterState();
  const currentPath = routerState.location.pathname;

  // Filter nav items based on role
  const filteredMainNav = useMemo(() => {
    if (!roleInfo) return [];
    return filterNavItems(mainNavItems, roleInfo.role);
  }, [roleInfo]);

  const filteredAdminNav = useMemo(() => {
    if (!roleInfo) return [];
    return filterNavItems(adminNavItems, roleInfo.role);
  }, [roleInfo]);

  const filteredSuperAdminNav = useMemo(() => {
    if (!roleInfo) return [];
    return filterNavItems(superAdminNavItems, roleInfo.role);
  }, [roleInfo]);

  const filteredBottomNav = useMemo(() => {
    if (!roleInfo) return [];
    return filterNavItems(bottomNavItems, roleInfo.role);
  }, [roleInfo]);

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div className="flex items-center gap-2 px-2 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-sm font-bold">L</span>
          </div>
          <span className="font-semibold group-data-[collapsible=icon]:hidden">
            Lockdev
          </span>
        </div>
        <div className="px-2 py-1 group-data-[collapsible=icon]:hidden">
          <OrgSwitcher />
        </div>
      </SidebarHeader>

      <SidebarContent>
        {/* Main Navigation */}
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {isLoading
                ? // Loading skeleton
                  Array.from({ length: 4 }).map((_, i) => (
                    <SidebarMenuItem key={i}>
                      <div className="flex items-center gap-2 px-2 py-1.5">
                        <Skeleton className="h-4 w-4" />
                        <Skeleton className="h-4 w-24 group-data-[collapsible=icon]:hidden" />
                      </div>
                    </SidebarMenuItem>
                  ))
                : filteredMainNav.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton
                        asChild
                        isActive={
                          currentPath === item.url ||
                          currentPath.startsWith(`${item.url}/`)
                        }
                        tooltip={item.title}
                      >
                        <Link to={item.url}>
                          <item.icon />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Admin Section - Only shown if user has admin items */}
        {filteredAdminNav.length > 0 && (
          <SidebarGroup>
            <SidebarGroupLabel>Organization</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {filteredAdminNav.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={
                        currentPath === item.url ||
                        currentPath.startsWith(`${item.url}/`)
                      }
                      tooltip={item.title}
                    >
                      <Link to={item.url}>
                        <item.icon />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {/* Super Admin Section */}
        {filteredSuperAdminNav.length > 0 && (
          <SidebarGroup>
            <SidebarGroupLabel>Platform</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {filteredSuperAdminNav.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={
                        currentPath === item.url ||
                        currentPath.startsWith(`${item.url}/`)
                      }
                      tooltip={item.title}
                    >
                      <Link to={item.url}>
                        <item.icon />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {/* Bottom Navigation (Settings, Help) */}
        <SidebarGroup className="mt-auto">
          <SidebarGroupContent>
            <SidebarMenu>
              {filteredBottomNav.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={
                      currentPath === item.url ||
                      currentPath.startsWith(`${item.url}/`)
                    }
                    tooltip={item.title}
                  >
                    <Link to={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <div className="px-2 py-1 group-data-[collapsible=icon]:hidden">
          <TimezoneDisplay />
        </div>
        <div className="flex items-center gap-2 px-2 py-2">
          <Avatar className="h-8 w-8">
            <AvatarImage src="" />
            <AvatarFallback className="text-xs">
              {user?.email?.charAt(0).toUpperCase() || "U"}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-1 flex-col group-data-[collapsible=icon]:hidden">
            <span className="text-sm font-medium truncate">
              {user?.displayName || user?.email?.split("@")[0] || "User"}
            </span>
            <span className="text-xs text-muted-foreground truncate">
              {user?.email}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 group-data-[collapsible=icon]:hidden"
            onClick={() => signOut()}
          >
            <LogOut className="h-4 w-4" />
            <span className="sr-only">Sign out</span>
          </Button>
        </div>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}
