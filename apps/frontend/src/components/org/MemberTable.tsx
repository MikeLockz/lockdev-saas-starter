import { Skeleton } from "@/components/ui/skeleton";
import { useTimezoneContext } from "@/contexts/TimezoneContext";

import { useCurrentOrg } from "@/hooks/useCurrentOrg";
import { useOrgMembers } from "@/hooks/useOrgMembers";
import { formatDateTime } from "@/lib/timezone";

// Since we don't have the shadcn table component installed yet, we'll use a local minimal version
// or just standard HTML if imports fail. But let's assume standard HTML with Tailwind classes
// similar to what shadcn would provide if I can't be sure it's there.
// Actually, earlier I saw I didn't have table.tsx.
// So I will implement a custom simple table here.

export function MemberTable() {
  const timezone = useTimezoneContext();
  const { orgId } = useCurrentOrg();
  const { data: members, isLoading } = useOrgMembers(orgId);

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-8 w-full" />
      </div>
    );
  }

  if (!members || members.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-muted-foreground border rounded-md">
        No members found in this organization.
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <table className="w-full caption-bottom text-sm">
        <thead className="[&_tr]:border-b">
          <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
              Name
            </th>
            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
              Email
            </th>
            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
              Role
            </th>
            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
              Joined At
            </th>
          </tr>
        </thead>
        <tbody className="[&_tr:last-child]:border-0">
          {members.map((member) => (
            <tr
              key={member.id}
              className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
            >
              <td className="p-4 align-middle font-medium">
                {member.display_name || "Unknown"}
              </td>
              <td className="p-4 align-middle">{member.email}</td>
              <td className="p-4 align-middle capitalize">{member.role}</td>
              <td className="p-4 align-middle">
                {member.created_at
                  ? formatDateTime(
                      new Date(member.created_at),
                      "MMM d, yyyy",
                      timezone,
                    )
                  : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
