import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter, useSegments } from "expo-router";
import {
  onAuthStateChange,
  getCurrentUserProfile,
  UserProfile,
  signOutUser,
} from "@/lib/firebase-auth";

type UseAuthOptions = {
  autoFetch?: boolean;
};

export interface User extends UserProfile {
  uid: string;
}

export function useAuth(options?: UseAuthOptions) {
  const { autoFetch = true } = options ?? {};
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const router = useRouter();
  const segments = useSegments();

  const fetchUser = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Listen to Firebase auth state changes
      const unsubscribe = onAuthStateChange(async (authUser) => {
        if (authUser) {
          try {
            const profile = await getCurrentUserProfile();
            if (profile) {
              setUser({ ...profile, uid: authUser.uid });
            }
          } catch (err) {
            const error = err instanceof Error ? err : new Error("Failed to fetch profile");
            console.error("[useAuth] Error fetching profile:", error);
            setError(error);
          }
        } else {
          setUser(null);
        }
        setLoading(false);
      });

      return unsubscribe;
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to initialize auth");
      console.error("[useAuth] fetchUser error:", error);
      setError(error);
      setUser(null);
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await signOutUser();
      setUser(null);
      setError(null);
      router.replace("/login");
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Logout failed");
      console.error("[Auth] Logout failed:", error);
      setError(error);
    }
  }, [router]);

  const isAuthenticated = useMemo(() => Boolean(user), [user]);

  useEffect(() => {
    if (autoFetch) {
      const unsubscribe = fetchUser();
      return () => {
        if (unsubscribe instanceof Promise) {
          unsubscribe.then((unsub) => unsub?.());
        } else if (typeof unsubscribe === "function") {
          unsubscribe();
        }
      };
    } else {
      setLoading(false);
    }
  }, [autoFetch, fetchUser]);

  // Handle navigation based on auth state
  useEffect(() => {
    if (loading) return;

    const inAuthGroup = segments[0] === "(auth)" || segments[0] === "login";

    if (!user && !inAuthGroup) {
      // Redirect to login if not authenticated
      router.replace("/login");
    } else if (user && inAuthGroup) {
      // Redirect to home if authenticated
      router.replace("/(tabs)");
    }
  }, [user, loading, segments, router]);



  return {
    user,
    loading,
    error,
    isAuthenticated,
    refresh: fetchUser,
    logout,
  };
}
