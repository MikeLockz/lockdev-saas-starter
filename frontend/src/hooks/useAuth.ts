import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from "@/lib/firebase";
import {
  GoogleAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
} from "firebase/auth";
import type { User } from "firebase/auth";
import { useState, useEffect } from "react";

const MOCK_USER_KEY = "lockdev_mock_user";

export function useAuth() {
  const [user, loading, error] = useAuthState(auth);
  const [mockUser, setMockUser] = useState<User | null>(null);

  // Check for mock user in local storage on mount
  useEffect(() => {
    const stored = localStorage.getItem(MOCK_USER_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Create a mock User object
      const mUser = {
        uid: "mock_uid",
        email: parsed.email,
        displayName: parsed.displayName,
        emailVerified: true,
        isAnonymous: false,
        metadata: {},
        providerData: [],
        refreshToken: "",
        tenantId: null,
        delete: async () => { },
        getIdToken: async () => `mock_${parsed.email}`,
        getIdTokenResult: async () => ({ token: `mock_${parsed.email}` } as any),
        reload: async () => { },
        toJSON: () => ({}),
        phoneNumber: null,
        photoURL: null,
        providerId: "mock",
      } as unknown as User;
      setMockUser(mUser);
    }
  }, []);

  const signInWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    try {
      return await signInWithPopup(auth, provider);
    } catch (err: unknown) {
      const error = err as { code?: string; message?: string };
      // Surface the error so user can see it
      console.error("Google Sign-in failed:", error.code, error.message);
      if (error.code === "auth/operation-not-allowed") {
        alert("Google Sign-in is not enabled in Firebase Console. Please enable it or use the 'E2E User' button for local development.");
      } else {
        alert(`Sign-in failed: ${error.message}`);
      }
      throw err;
    }
  };

  const signInDev = (email: string, displayName: string) => {
    localStorage.setItem(MOCK_USER_KEY, JSON.stringify({ email, displayName }));
    window.location.reload(); // Reload to pick up the mock user state
  };

  const signOut = async () => {
    if (mockUser) {
      localStorage.removeItem(MOCK_USER_KEY);
      setMockUser(null);
      window.location.reload();
    } else {
      return firebaseSignOut(auth);
    }
  };

  return {
    user: mockUser || user,
    loading: loading && !mockUser,
    error,
    signInWithGoogle,
    signInDev,
    signOut,
  };
}
