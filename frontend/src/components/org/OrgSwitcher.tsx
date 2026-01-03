import { ChevronsUpDown, Check, Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
    DropdownMenuGroup,
} from "@/components/ui/dropdown-menu"
import { useCurrentOrg } from "@/hooks/useCurrentOrg"
import { cn } from "@/lib/utils"

export function OrgSwitcher() {
    const { organization, organizations, setCurrentOrgId, isLoading } = useCurrentOrg()

    // If loading or no organizations, maybe show a skeleton or simplified view
    // For now, we'll just handle empty state

    const currentOrgName = organization?.name || "Select Organization"

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button
                    variant="outline"
                    role="combobox"
                    aria-label="Select organization"
                    className="w-[200px] justify-between"
                    disabled={isLoading}
                >
                    <span className="truncate">{currentOrgName}</span>
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-[200px]">
                <DropdownMenuLabel>Organizations</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuGroup>
                    {organizations?.map((org) => (
                        <DropdownMenuItem
                            key={org.id}
                            onSelect={() => setCurrentOrgId(org.id)}
                        >
                            <Check
                                className={cn(
                                    "mr-2 h-4 w-4",
                                    org.id === organization?.id ? "opacity-100" : "opacity-0"
                                )}
                            />
                            <span className="truncate">{org.name}</span>
                        </DropdownMenuItem>
                    ))}
                    {(!organizations || organizations.length === 0) && (
                        <DropdownMenuItem disabled>No organizations found</DropdownMenuItem>
                    )}
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={() => console.log("Create Org clicked")}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Organization
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
