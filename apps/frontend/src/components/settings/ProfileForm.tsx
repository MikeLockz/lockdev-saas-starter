import { useState } from "react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useUserProfile } from "@/hooks/useUserProfile";

export function ProfileForm() {
  const { profile, updateProfile } = useUserProfile();
  const [displayName, setDisplayName] = useState(
    profile?.display_name || profile?.full_name || "",
  );
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const getInitials = (name?: string, email?: string) => {
    if (name) {
      return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    return email?.slice(0, 2).toUpperCase() || "U";
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateProfile.mutateAsync({ display_name: displayName });
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to update profile:", error);
    } finally {
      setIsSaving(false);
    }
  };

  if (!profile) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-20 w-20 rounded-full bg-muted" />
            <div className="h-4 w-48 bg-muted rounded" />
            <div className="h-4 w-32 bg-muted rounded" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile Information</CardTitle>
        <CardDescription>Manage your personal details</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center gap-4">
          <Avatar className="h-20 w-20">
            <AvatarFallback className="text-2xl">
              {getInitials(
                profile.display_name || profile.full_name,
                profile.email,
              )}
            </AvatarFallback>
          </Avatar>
          <div>
            <p className="text-lg font-medium">
              {profile.display_name || profile.full_name || "No name set"}
            </p>
            <p className="text-sm text-muted-foreground">{profile.email}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              value={profile.email}
              disabled
              className="bg-muted"
            />
            <p className="text-xs text-muted-foreground">
              Email cannot be changed
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="displayName">Display Name</Label>
            {isEditing ? (
              <div className="flex gap-2">
                <Input
                  id="displayName"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="Enter your name"
                />
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving ? "Saving..." : "Save"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsEditing(false);
                    setDisplayName(
                      profile.display_name || profile.full_name || "",
                    );
                  }}
                >
                  Cancel
                </Button>
              </div>
            ) : (
              <div className="flex gap-2 items-center">
                <Input
                  id="displayName"
                  value={profile.display_name || profile.full_name || ""}
                  disabled
                  className="bg-muted"
                />
                <Button variant="outline" onClick={() => setIsEditing(true)}>
                  Edit
                </Button>
              </div>
            )}
          </div>
        </div>

        <div className="border-t pt-4 space-y-2">
          <p className="text-sm text-muted-foreground">
            Account created: {new Date(profile.created_at).toLocaleDateString()}
          </p>
          <p className="text-sm text-muted-foreground">
            Last updated: {new Date(profile.updated_at).toLocaleDateString()}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
