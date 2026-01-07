import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

interface PermissionToggleProps {
  label: string;
  description?: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
}

export function PermissionToggle({
  label,
  description,
  checked,
  onCheckedChange,
  disabled = false,
}: PermissionToggleProps) {
  return (
    <div className="flex items-center justify-between space-x-4 py-3 px-4 rounded-lg hover:bg-muted/50 transition-colors">
      <div className="space-y-0.5">
        <Label className="text-sm font-medium cursor-pointer">{label}</Label>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
      <Switch
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
        aria-label={label}
      />
    </div>
  );
}

// Permission categories for organized display
export const PERMISSION_CATEGORIES = {
  view: {
    label: "View Access",
    permissions: [
      {
        key: "can_view_profile",
        label: "View Profile",
        description: "Access basic patient information",
      },
      {
        key: "can_view_appointments",
        label: "View Appointments",
        description: "See scheduled appointments",
      },
      {
        key: "can_view_clinical_notes",
        label: "View Clinical Notes",
        description: "Access medical notes and records",
      },
      {
        key: "can_view_billing",
        label: "View Billing",
        description: "Access billing statements and invoices",
      },
    ],
  },
  actions: {
    label: "Actions",
    permissions: [
      {
        key: "can_schedule_appointments",
        label: "Schedule Appointments",
        description: "Book and manage appointments",
      },
      {
        key: "can_message_providers",
        label: "Message Providers",
        description: "Send messages to care team",
      },
    ],
  },
} as const;

interface PermissionGroupProps {
  category: keyof typeof PERMISSION_CATEGORIES;
  permissions: { [key: string]: boolean };
  onPermissionChange: (key: string, value: boolean) => void;
  disabled?: boolean;
}

export function PermissionGroup({
  category,
  permissions,
  onPermissionChange,
  disabled = false,
}: PermissionGroupProps) {
  const categoryConfig = PERMISSION_CATEGORIES[category];

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
        {categoryConfig.label}
      </h4>
      <div className="space-y-1 border rounded-lg">
        {categoryConfig.permissions.map((perm) => (
          <PermissionToggle
            key={perm.key}
            label={perm.label}
            description={perm.description}
            checked={permissions[perm.key] ?? false}
            onCheckedChange={(checked) => onPermissionChange(perm.key, checked)}
            disabled={disabled}
          />
        ))}
      </div>
    </div>
  );
}
