import { useMyProxyPatients } from "@/hooks/api/useMyProxyPatients";
import { ProxyPatientCard } from "@/components/proxies/ProxyPatientCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Users } from "lucide-react";

export default function ProxyPatientsPage() {
    const { data: proxyPatients, isLoading, error } = useMyProxyPatients();

    if (isLoading) {
        return (
            <div className="container py-6 space-y-6">
                <Skeleton className="h-8 w-64" />
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {[1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-48 w-full" />
                    ))}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container py-6">
                <div className="text-center text-destructive">
                    Error loading patients. Please try again.
                </div>
            </div>
        );
    }

    return (
        <div className="container py-6 space-y-6">
            <div>
                <h1 className="text-2xl font-bold">My Patients</h1>
                <p className="text-muted-foreground">
                    Patients you're authorized to manage as a proxy
                </p>
            </div>

            {proxyPatients && proxyPatients.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {proxyPatients.map((proxyPatient) => (
                        <ProxyPatientCard
                            key={proxyPatient.patient.id}
                            proxyPatient={proxyPatient}
                        />
                    ))}
                </div>
            ) : (
                <div className="text-center py-12 border rounded-lg">
                    <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <h2 className="text-lg font-medium mb-2">No Patients</h2>
                    <p className="text-muted-foreground">
                        You are not currently assigned as a proxy for any patients.
                    </p>
                </div>
            )}
        </div>
    );
}
