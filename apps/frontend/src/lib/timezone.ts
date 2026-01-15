/**
 * Timezone utilities for date/time formatting.
 * Uses date-fns-tz for timezone-aware operations.
 */

import { formatDistanceToNow } from "date-fns";
import { formatInTimeZone, toZonedTime } from "date-fns-tz";

/**
 * Format a date/time in the specified timezone.
 *
 * @param date - Date object, ISO string, or timestamp
 * @param formatStr - date-fns format string (e.g., 'PPpp' for full date/time)
 * @param timezone - IANA timezone identifier (e.g., 'America/New_York')
 * @returns Formatted date string in the specified timezone
 *
 * @example
 * formatDateTime(new Date(), 'PPpp', 'America/New_York')
 * // "Jan 4, 2026, 3:45 PM EST"
 */
export function formatDateTime(
  date: Date | string | number,
  formatStr: string,
  timezone: string,
): string {
  return formatInTimeZone(date, timezone, formatStr);
}

/**
 * Format a date/time as a relative time string (e.g., "5 minutes ago").
 * The time is first converted to the specified timezone for accuracy.
 *
 * @param date - Date object, ISO string, or timestamp
 * @param timezone - IANA timezone identifier
 * @returns Relative time string with suffix (e.g., "in 5 minutes", "3 hours ago")
 */
export function formatRelativeTime(
  date: Date | string | number,
  timezone: string,
): string {
  const dateObj =
    typeof date === "string" || typeof date === "number"
      ? new Date(date)
      : date;
  const zonedDate = toZonedTime(dateObj, timezone);
  return formatDistanceToNow(zonedDate, { addSuffix: true });
}

/**
 * Common format strings for consistency across the app.
 */
export const DATE_FORMATS = {
  /** Full date with time: "Jan 4, 2026, 3:45 PM" */
  FULL: "PPpp",
  /** Date only: "Jan 4, 2026" */
  DATE: "PP",
  /** Time only: "3:45 PM" */
  TIME: "p",
  /** Short date: "1/4/2026" */
  SHORT_DATE: "P",
  /** Short date with time: "1/4/2026, 3:45 PM" */
  SHORT_DATETIME: "Pp",
  /** Day and time: "Mon, 3:45 PM" */
  DAY_TIME: "EEE, p",
  /** Month and day: "Jan 4" */
  MONTH_DAY: "MMM d",
  /** Full month, day, year: "January 4, 2026" */
  LONG_DATE: "MMMM d, yyyy",
  /** ISO format: "2026-01-04" */
  ISO_DATE: "yyyy-MM-dd",
};

/**
 * Get the UTC offset for display (e.g., "UTC-5").
 *
 * @param timezone - IANA timezone identifier
 * @param date - Optional date for DST-aware offset (defaults to now)
 * @returns Formatted UTC offset string
 */
export function getTimezoneOffset(
  timezone: string,
  date: Date = new Date(),
): string {
  try {
    const formatted = formatInTimeZone(date, timezone, "xxx");
    return `UTC${formatted}`;
  } catch {
    return "UTC";
  }
}

/**
 * Timezone display names for the UI.
 */
export const TIMEZONE_DISPLAY: Record<string, string> = {
  "America/New_York": "Eastern Time (ET)",
  "America/Chicago": "Central Time (CT)",
  "America/Denver": "Mountain Time (MT)",
  "America/Phoenix": "Arizona Time",
  "America/Los_Angeles": "Pacific Time (PT)",
  "America/Anchorage": "Alaska Time",
  "Pacific/Honolulu": "Hawaii Time",
  "America/Toronto": "Toronto (ET)",
  "America/Vancouver": "Vancouver (PT)",
  "Europe/London": "London (GMT/BST)",
  "Europe/Paris": "Paris (CET/CEST)",
  "Europe/Berlin": "Berlin (CET/CEST)",
  "Asia/Tokyo": "Tokyo (JST)",
  "Asia/Shanghai": "Shanghai (CST)",
  "Asia/Singapore": "Singapore (SGT)",
  "Australia/Sydney": "Sydney (AEST/AEDT)",
  UTC: "UTC",
};

/**
 * Get friendly display name for a timezone.
 */
export function getTimezoneDisplayName(timezone: string): string {
  return (
    TIMEZONE_DISPLAY[timezone] ||
    timezone.replace("_", " ").split("/").pop() ||
    timezone
  );
}
