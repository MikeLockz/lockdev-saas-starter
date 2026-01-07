/**
 * TimezoneSelector component for selecting timezone from list.
 * Provides search/filter functionality and grouped display.
 */

import { Check, ChevronsUpDown, Globe } from "lucide-react";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { getTimezoneDisplayName, getTimezoneOffset } from "@/lib/timezone";
import { cn } from "@/lib/utils";

/**
 * IANA timezone identifiers grouped by region.
 */
const TIMEZONE_GROUPS = {
  "North America": [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Phoenix",
    "America/Los_Angeles",
    "America/Anchorage",
    "Pacific/Honolulu",
    "America/Toronto",
    "America/Vancouver",
  ],
  Europe: [
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Europe/Madrid",
    "Europe/Rome",
    "Europe/Amsterdam",
    "Europe/Brussels",
    "Europe/Vienna",
    "Europe/Warsaw",
    "Europe/Athens",
  ],
  Asia: [
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Singapore",
    "Asia/Hong_Kong",
    "Asia/Seoul",
    "Asia/Kolkata",
    "Asia/Dubai",
    "Asia/Bangkok",
    "Asia/Manila",
  ],
  Oceania: [
    "Australia/Sydney",
    "Australia/Melbourne",
    "Australia/Brisbane",
    "Australia/Perth",
    "Pacific/Auckland",
  ],
  Other: ["UTC"],
};

interface TimezoneSelectorProps {
  value: string;
  onChange: (timezone: string) => void;
  disabled?: boolean;
  className?: string;
}

export function TimezoneSelector({
  value,
  onChange,
  disabled = false,
  className,
}: TimezoneSelectorProps) {
  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Filter timezones based on search
  const filteredGroups = useMemo(() => {
    if (!searchQuery) return TIMEZONE_GROUPS;

    const query = searchQuery.toLowerCase();
    const result: Record<string, string[]> = {};

    for (const [group, timezones] of Object.entries(TIMEZONE_GROUPS)) {
      const filtered = timezones.filter((tz) => {
        const label = getTimezoneDisplayName(tz).toLowerCase();
        const offset = getTimezoneOffset(tz).toLowerCase();
        return (
          tz.toLowerCase().includes(query) ||
          label.includes(query) ||
          offset.includes(query)
        );
      });
      if (filtered.length > 0) {
        result[group] = filtered;
      }
    }
    return result;
  }, [searchQuery]);

  const selectedLabel = value
    ? getTimezoneDisplayName(value)
    : "Select timezone...";
  const selectedOffset = value ? getTimezoneOffset(value) : "";

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className={cn("w-full justify-between font-normal", className)}
        >
          <div className="flex items-center gap-2 truncate">
            <Globe className="h-4 w-4 text-muted-foreground shrink-0" />
            <span className="truncate">{selectedLabel}</span>
            {selectedOffset && (
              <span className="text-xs text-muted-foreground shrink-0">
                ({selectedOffset})
              </span>
            )}
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder="Search timezones..."
            value={searchQuery}
            onValueChange={setSearchQuery}
          />
          <CommandList className="max-h-[300px]">
            <CommandEmpty>No timezone found.</CommandEmpty>
            {Object.entries(filteredGroups).map(([group, timezones]) => (
              <CommandGroup key={group} heading={group}>
                {timezones.map((tz) => (
                  <CommandItem
                    key={tz}
                    value={tz}
                    onSelect={() => {
                      onChange(tz);
                      setOpen(false);
                      setSearchQuery("");
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === tz ? "opacity-100" : "opacity-0",
                      )}
                    />
                    <div className="flex-1 flex justify-between items-center">
                      <span>{getTimezoneDisplayName(tz)}</span>
                      <span className="text-xs text-muted-foreground">
                        {getTimezoneOffset(tz)}
                      </span>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            ))}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
