import { AlertCircle } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useRequiredConsents } from "@/hooks/api/useRequiredConsents";
import { useSignConsent } from "@/hooks/api/useSignConsent";
import { ConsentDocument } from "./ConsentDocument";

interface ConsentListProps {
  onComplete: () => void;
}

export function ConsentList({ onComplete }: ConsentListProps) {
  const { data: consents, isLoading, error, refetch } = useRequiredConsents();
  const { mutate: signConsent, isPending } = useSignConsent();
  const [signedIds, setSignedIds] = useState<Set<string>>(new Set());

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-12">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <h2 className="text-lg font-semibold">
          Failed to load consent documents
        </h2>
        <p className="text-muted-foreground">{error.message}</p>
        <Button onClick={() => refetch()}>Try Again</Button>
      </div>
    );
  }

  if (!consents || consents.length === 0) {
    // No consents needed, proceed
    onComplete();
    return null;
  }

  const handleSign = (documentId: string, checked: boolean) => {
    if (!checked) return;

    signConsent(documentId, {
      onSuccess: () => {
        setSignedIds((prev) => new Set([...prev, documentId]));
        toast.success("Consent signed successfully");

        // Check if all are signed
        if (signedIds.size + 1 >= consents.length) {
          onComplete();
        }
      },
      onError: (error) => {
        toast.error(`Failed to sign consent: ${error.message}`);
      },
    });
  };

  const allSigned = signedIds.size >= consents.length;

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {consents.map((consent) => (
          <ConsentDocument
            key={consent.document_id}
            id={consent.document_id}
            title={consent.title}
            documentType={consent.document_type}
            versionId={consent.version_id}
            isSigned={signedIds.has(consent.document_id)}
            onSign={handleSign}
          />
        ))}
      </div>

      {allSigned && (
        <div className="flex justify-center">
          <Button onClick={onComplete} size="lg">
            Continue to Dashboard
          </Button>
        </div>
      )}

      {isPending && (
        <p className="text-center text-sm text-muted-foreground">
          Signing consent...
        </p>
      )}
    </div>
  );
}
