import { useState } from 'react';
import { createFileRoute, Link } from '@tanstack/react-router';
import { ProfileForm, SessionList, MFASetup, PreferencesForm } from '@/components/settings';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';

const TABS = [
  { id: 'profile', label: 'Profile', icon: '👤' },
  { id: 'security', label: 'Security', icon: '🔒' },
  { id: 'privacy', label: 'Privacy', icon: '🔔' },
] as const;

type TabId = (typeof TABS)[number]['id'];

export const Route = createFileRoute('/_auth/settings')({
  component: Settings,
});

export function Settings() {
  const [activeTab, setActiveTab] = useState<TabId>('profile');
  const { user, signOut } = useAuth();

  const handleLogout = async () => {
    await signOut();
  };

  return (
    <div className="min-h-screen bg-muted/30">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/dashboard" className="text-lg font-semibold hover:text-primary">
              ← Back to Dashboard
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground mt-1">
            Manage your account settings and preferences
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Tabs */}
          <nav className="lg:w-64 space-y-1">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors
                  ${activeTab === tab.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted'
                  }
                `}
              >
                <span>{tab.icon}</span>
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </nav>

          {/* Tab Content */}
          <div className="flex-1 min-w-0 max-w-3xl">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <ProfileForm />
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <SessionList />
                <MFASetup />
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <PreferencesForm />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
