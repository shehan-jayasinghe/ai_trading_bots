"use client";

import { AuthSync } from "@/components/auth-sync";
import { Toaster } from "@/components/ui/sonner";
import { SessionProvider } from "next-auth/react";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <AuthSync />
      {children}
      <Toaster />
    </SessionProvider>
  );
}
