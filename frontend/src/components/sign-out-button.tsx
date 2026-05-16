"use client";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";
import { signOut } from "next-auth/react";

export function SignOutButton() {
  const clearAuth = useAuthStore((s) => s.clearAuth);

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      onClick={() => {
        clearAuth();
        void signOut({ callbackUrl: "/login" });
      }}
    >
      Sign out
    </Button>
  );
}
