import { auth } from "@/lib/firebase";
import { signOut as firebaseSignOut, signInWithEmailAndPassword } from "firebase/auth";
import { useAuthState } from "react-firebase-hooks/auth";

export const useAuth = () => {
  const [user, loading, error] = useAuthState(auth);

  const signIn = async (email: string, pass: string) => {
    return signInWithEmailAndPassword(auth, email, pass);
  };

  const signOut = async () => {
    return firebaseSignOut(auth);
  };

  return {
    user,
    loading,
    error,
    signIn,
    signOut,
  };
};
