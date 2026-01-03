import { useState } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { ProviderTable } from '@/components/providers/ProviderTable'
import { ProviderForm } from '@/components/providers/ProviderForm'
import type { ProviderListItem } from '@/hooks/useProviders'

export const Route = createFileRoute('/_auth/admin/providers')({
    component: ProvidersPage,
})

function ProvidersPage() {
    const [isFormOpen, setIsFormOpen] = useState(false)
    const [selectedProvider, setSelectedProvider] = useState<ProviderListItem | null>(null)

    const handleCreate = () => {
        setSelectedProvider(null)
        setIsFormOpen(true)
    }

    const handleEdit = (provider: ProviderListItem) => {
        setSelectedProvider(provider)
        setIsFormOpen(true)
    }

    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-medium">Providers</h3>
                <p className="text-sm text-muted-foreground">
                    Manage healthcare providers and their credentials.
                </p>
            </div>

            <ProviderTable
                onCreate={handleCreate}
                onEdit={handleEdit}
            />

            <ProviderForm
                open={isFormOpen}
                onOpenChange={setIsFormOpen}
                provider={selectedProvider}
            />
        </div>
    )
}
