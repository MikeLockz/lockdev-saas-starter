import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface SessionExpiryModalProps {
    isOpen: boolean;
    timeRemaining: number;
    onExtend: () => void;
    onLogout: () => void;
}

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function SessionExpiryModal({
    isOpen,
    timeRemaining,
    onExtend,
    onLogout,
}: SessionExpiryModalProps) {
    return (
        <Dialog open={isOpen}>
            <DialogContent className="sm:max-w-md" onPointerDownOutside={(e) => e.preventDefault()}>
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <span className="text-2xl">⏱️</span>
                        Session Expiring Soon
                    </DialogTitle>
                    <DialogDescription className="text-base pt-2">
                        For your security, your session will expire due to inactivity.
                    </DialogDescription>
                </DialogHeader>

                <div className="py-6">
                    <div className="text-center">
                        <p className="text-sm text-muted-foreground mb-2">
                            Time remaining before automatic logout:
                        </p>
                        <p className="text-4xl font-mono font-bold text-primary">
                            {formatTime(timeRemaining)}
                        </p>
                    </div>
                </div>

                <DialogFooter className="flex gap-2 sm:gap-2">
                    <Button variant="outline" onClick={onLogout}>
                        Logout Now
                    </Button>
                    <Button onClick={onExtend}>
                        Stay Logged In
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
