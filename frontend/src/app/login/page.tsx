import { Suspense } from "react";
import { LoginForm } from "./login-form";

export default function LoginPage() {
  return (
    <div className="min-h-full flex-1 bg-slate-950 text-slate-50">
      <Suspense
        fallback={
          <div className="flex min-h-[50vh] items-center justify-center text-sm text-slate-500">
            Loading…
          </div>
        }
      >
        <LoginForm />
      </Suspense>
    </div>
  );
}
