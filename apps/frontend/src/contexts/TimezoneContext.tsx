/**
 * Timezone Context for providing timezone throughout the app.
 */
import { createContext, type ReactNode, useContext } from "react";
import { useTimezone } from "@/hooks/useTimezone";

const DEFAULT_TIMEZONE = "America/New_York";

const TimezoneContext = createContext<string>(DEFAULT_TIMEZONE);

interface TimezoneProviderProps {
  children: ReactNode;
}

/**
 * Provider that makes the user's effective timezone available throughout the app.
 * Uses the useTimezone hook to fetch from the API.
 */
export function TimezoneProvider({ children }: TimezoneProviderProps) {
  const timezone = useTimezone();

  return (
    <TimezoneContext.Provider value={timezone}>
      {children}
    </TimezoneContext.Provider>
  );
}

/**
 * Hook to access the current timezone from context.
 * Must be used within a TimezoneProvider.
 */
export function useTimezoneContext(): string {
  return useContext(TimezoneContext);
}

/**
 * Export the raw context for advanced usage.
 */
export { TimezoneContext };
