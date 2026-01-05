/**
 * TimezoneDisplay component for showing current timezone in header/settings.
 */
import { Globe } from 'lucide-react';
import { useTimezoneWithSource } from '@/hooks/useTimezone';
import { getTimezoneDisplayName, getTimezoneOffset } from '@/lib/timezone';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';

interface TimezoneDisplayProps {
    showLabel?: boolean;
    className?: string;
}

export function TimezoneDisplay({ showLabel = true, className }: TimezoneDisplayProps) {
    const { data, isLoading } = useTimezoneWithSource();

    if (isLoading) {
        return <Skeleton className="h-5 w-24" />;
    }

    const timezone = data?.timezone || 'America/New_York';
    const source = data?.source || 'organization';
    const displayName = getTimezoneDisplayName(timezone);
    const offset = getTimezoneOffset(timezone);

    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <div className={`flex items-center gap-1.5 text-muted-foreground text-sm ${className}`}>
                        <Globe className="h-3.5 w-3.5" />
                        {showLabel && (
                            <>
                                <span className="hidden sm:inline">{displayName}</span>
                                <span className="sm:hidden">{offset}</span>
                            </>
                        )}
                        {!showLabel && <span>{offset}</span>}
                    </div>
                </TooltipTrigger>
                <TooltipContent>
                    <div className="text-sm">
                        <p className="font-medium">{displayName}</p>
                        <p className="text-muted-foreground">{offset}</p>
                        <Badge variant="outline" className="mt-1 text-[10px]">
                            {source === 'user' ? 'Personal preference' : 'Organization default'}
                        </Badge>
                    </div>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}
