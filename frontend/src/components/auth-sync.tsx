"use client";

import { fetchAccessToken } from "@/services/auth.service";
import { useAuthStore } from "@/stores/auth-store";
import { useSession } from "next-auth/react";
import { useEffect, useRef } from "react";

export function AuthSync() {
  const { data: session, status } = useSession();
  const setAuth = useAuthStore((s) => s.setAuth);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const fetchedForUserId = useRef<string | null>(null);

  useEffect(() => {
    if (status === "loading") return;

    if (status === "unauthenticated") {
      clearAuth();
      fetchedForUserId.current = null;
      return;
    }

    const userId = session?.user?.id;
    if (!userId || fetchedForUserId.current === userId) return;

    let cancelled = false;

    async function sync() {
      try {
        const data = await fetchAccessToken();
        if (!cancelled && data.token && userId) {
          setAuth(data.user, data.token);
          fetchedForUserId.current = userId;
        }
      } catch {
        if (!cancelled) clearAuth();
      }
    }

    void sync();
    return () => {
      cancelled = true;
    };
  }, [session, status, setAuth, clearAuth]);

  return null;
}
