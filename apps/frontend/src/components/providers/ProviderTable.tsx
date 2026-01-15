import { Edit2, Plus, Search, Trash2 } from "lucide-react";
import { useState } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  type ProviderListItem,
  useDeleteProvider,
  useProviders,
} from "@/hooks/useProviders";

interface ProviderTableProps {
  onEdit?: (provider: ProviderListItem) => void;
  onCreate?: () => void;
}

export function ProviderTable({ onEdit, onCreate }: ProviderTableProps) {
  const [searchSpecialty, setSearchSpecialty] = useState("");
  const [deleteId, setDeleteId] = useState<string | null>(null);

  // Hooks
  const { data, isLoading } = useProviders({
    specialty: searchSpecialty || undefined,
  });
  const deleteProvider = useDeleteProvider();

  // Handlers
  const handleDelete = async () => {
    if (deleteId) {
      await deleteProvider.mutateAsync(deleteId);
      setDeleteId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header Actions */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Filter by specialty..."
            value={searchSpecialty}
            onChange={(e) => setSearchSpecialty(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button onClick={onCreate}>
          <Plus className="mr-2 h-4 w-4" />
          Add Provider
        </Button>
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Specialty</TableHead>
              <TableHead>NPI</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Skeleton className="h-4 w-32" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-24" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-20" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-16" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-8 ml-auto" />
                  </TableCell>
                </TableRow>
              ))
            ) : data?.items.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-center py-8 text-muted-foreground"
                >
                  No providers found
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((provider) => (
                <TableRow key={provider.id}>
                  <TableCell className="font-medium">
                    {provider.user_display_name || provider.user_email}
                  </TableCell>
                  <TableCell>{provider.specialty || "—"}</TableCell>
                  <TableCell className="font-mono text-sm">
                    {provider.npi_number || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={provider.is_active ? "default" : "secondary"}
                    >
                      {provider.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onEdit?.(provider)}
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-destructive"
                        onClick={() => setDeleteId(provider.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Delete Confirmation */}
      <AlertDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will remove the provider profile. The user account will
              remain active.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={handleDelete}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
