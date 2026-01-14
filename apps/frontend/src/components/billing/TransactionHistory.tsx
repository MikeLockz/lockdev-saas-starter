import { Download } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { usePatientTransactions } from "@/hooks/api/usePatientBilling";
import { formatCurrency, formatDate } from "@/lib/utils";

interface Props {
  patientId: string;
}

export function TransactionHistory({ patientId }: Props) {
  const { data, isLoading } = usePatientTransactions(patientId);

  const getStatusBadge = (status: string) => {
    const variants: Record<
      string,
      "default" | "destructive" | "outline" | "secondary"
    > = {
      SUCCEEDED: "default",
      PENDING: "secondary",
      FAILED: "destructive",
      REFUNDED: "outline",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  if (isLoading) {
    return <div>Loading transactions...</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transaction History</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Receipt</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.transactions.map((tx) => (
              <TableRow key={tx.id}>
                <TableCell>{formatDate(new Date(tx.created_at))}</TableCell>
                <TableCell>
                  {tx.description || "Subscription Payment"}
                </TableCell>
                <TableCell>{formatCurrency(tx.amount_cents / 100)}</TableCell>
                <TableCell>{getStatusBadge(tx.status)}</TableCell>
                <TableCell>
                  {tx.receipt_url && (
                    <Button variant="ghost" size="sm" asChild>
                      <a
                        href={tx.receipt_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Receipt
                      </a>
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
            {!data?.transactions.length && (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-center py-4 text-muted-foreground"
                >
                  No transactions found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
