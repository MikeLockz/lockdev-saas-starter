import { createFileRoute, Link } from "@tanstack/react-router";
import { Building, Camera, Lock } from "lucide-react";
import { useState } from "react";
import {
  MFASetup,
  PreferencesForm,
  ProfileForm,
  SessionList,
  TimezonePreferences,
} from "@/components/settings";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";

const TABS = [
  { id: "profile", label: "Profile", icon: "👤" },
  { id: "security", label: "Security", icon: "🔒" },
  { id: "privacy", label: "Privacy", icon: "🔔" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export const Route = createFileRoute("/_auth/settings")({
  component: Settings,
});

export function Settings() {
  const [activeTab, setActiveTab] = useState<TabId>("profile");
  const { user, signOut } = useAuth();
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);

  const handleLogout = async () => {
    await signOut();
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Create object URL for preview
      const url = URL.createObjectURL(file);
      setPhotoUrl(url);
      // TODO: Upload to server
    }
  };

  const getInitials = (name?: string | null, email?: string | null) => {
    if (name) return name.slice(0, 2).toUpperCase();
    if (email) return email.slice(0, 2).toUpperCase();
    return "U";
  };

  return (
    <div className="min-h-screen bg-muted/30">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/dashboard"
              className="text-lg font-semibold hover:text-primary"
            >
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
                type="button"
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors
                  ${
                    activeTab === tab.id
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }
                `}
              >
                <span>{tab.icon}</span>
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}

            {/* Organizations Link */}
            <Link
              to="/settings/organizations"
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors hover:bg-muted"
            >
              <Building className="h-4 w-4" />
              <span className="font-medium">Organizations</span>
            </Link>
          </nav>

          {/* Tab Content */}
          <div className="flex-1 min-w-0 max-w-3xl">
            {activeTab === "profile" && (
              <div className="space-y-6">
                {/* Photo Upload Section */}
                <Card>
                  <CardHeader>
                    <CardTitle>Profile Photo</CardTitle>
                    <CardDescription>
                      Update your profile picture
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-4">
                      <Avatar className="h-20 w-20">
                        <AvatarImage src={photoUrl || undefined} />
                        <AvatarFallback className="text-2xl">
                          {getInitials(user?.displayName, user?.email)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <Button
                          variant="outline"
                          onClick={() =>
                            document.getElementById("photo-upload")?.click()
                          }
                        >
                          <Camera className="h-4 w-4 mr-2" />
                          Upload Photo
                        </Button>
                        <input
                          id="photo-upload"
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={handlePhotoUpload}
                        />
                        <p className="text-sm text-muted-foreground mt-2">
                          JPG, PNG or GIF. Max 2MB.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <ProfileForm />
              </div>
            )}

            {activeTab === "security" && (
              <div className="space-y-6">
                {/* Password Change Section */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lock className="h-5 w-5" />
                      Password
                    </CardTitle>
                    <CardDescription>
                      Change your account password
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button onClick={() => setPasswordModalOpen(true)}>
                      Change Password
                    </Button>
                  </CardContent>
                </Card>
                <SessionList />
                <MFASetup />
              </div>
            )}

            {activeTab === "privacy" && (
              <div className="space-y-6">
                <TimezonePreferences />
                <PreferencesForm />
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Password Change Modal */}
      <Dialog open={passwordModalOpen} onOpenChange={setPasswordModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change Password</DialogTitle>
            <DialogDescription>
              Enter your current password and choose a new one
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="current">Current Password</Label>
              <Input id="current" type="password" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new">New Password</Label>
              <Input id="new" type="password" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm">Confirm New Password</Label>
              <Input id="confirm" type="password" />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setPasswordModalOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={() => setPasswordModalOpen(false)}>
              Update Password
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
