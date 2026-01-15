import { Link } from "@tanstack/react-router";
import { FileQuestion } from "lucide-react";
import { Button } from "@/components/ui/button";

export function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/30 px-4">
      <div className="text-center space-y-6 max-w-md">
        {/* Logo/Brand */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-xl">L</span>
          </div>
          <span className="text-2xl font-bold">Lockdev</span>
        </div>

        {/* Icon */}
        <div className="flex justify-center">
          <div className="bg-muted rounded-full p-6">
            <FileQuestion className="h-16 w-16 text-muted-foreground" />
          </div>
        </div>

        {/* Message */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Page Not Found</h1>
          <p className="text-muted-foreground text-lg">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-4">
          <Button asChild size="lg">
            <Link to="/dashboard">Return to Dashboard</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link to="/">Go to Home</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
