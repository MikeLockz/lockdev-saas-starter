import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface ConsentDocumentProps {
  id: string;
  title: string;
  documentType: string;
  versionId: string;
  isSigned: boolean;
  onSign: (id: string, checked: boolean) => void;
}

export function ConsentDocument({
  id,
  title,
  documentType,
  versionId,
  isSigned,
  onSign,
}: ConsentDocumentProps) {
  return (
    <Card className={isSigned ? "border-green-500" : ""}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          {title || documentType}
          {isSigned && (
            <span className="text-sm text-green-600 font-normal">✓ Signed</span>
          )}
        </CardTitle>
        <CardDescription>Version {versionId}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-md border p-4 h-32 overflow-y-auto">
          <p className="text-sm text-muted-foreground">
            Please review and accept this consent document to continue using the
            application. This document covers important terms regarding your use
            of our healthcare services.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id={`consent-${id}`}
            checked={isSigned}
            onChange={(e) => onSign(id, e.target.checked)}
            disabled={isSigned}
            className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
          />
          <label
            htmlFor={`consent-${id}`}
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            I have read and agree to the terms outlined in this document
          </label>
        </div>
      </CardContent>
    </Card>
  );
}
