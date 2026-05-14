"use client";

import { loginFormSchema, zodIssuesToFieldErrors } from "@/lib/validation";
import { signIn } from "next-auth/react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const urlError = searchParams.get("error");
  const urlErrorMessage =
    urlError === "CredentialsSignin"
      ? "Invalid email or password."
      : urlError
        ? "Sign in failed. Please try again."
        : null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const parsed = loginFormSchema.safeParse({ email, password });
    if (!parsed.success) {
      setFieldErrors(zodIssuesToFieldErrors(parsed.error));
      return;
    }
    setFieldErrors({});

    setLoading(true);
    try {
      const res = await signIn("credentials", {
        email: parsed.data.email,
        password: parsed.data.password,
        redirect: false,
      });

      if (res?.error) {
        setFormError("Invalid email or password.");
        return;
      }
      if (res?.ok) {
        router.push("/");
        router.refresh();
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-full flex-1 flex-col justify-center px-4 py-14">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/40 via-slate-950 to-slate-950"
        aria-hidden
      />
      <div className="relative mx-auto w-full max-w-md">
        <div className="mb-10 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-400/90">
            Deriv AI
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">
            Sign in
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Email and password to continue
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-white/10 bg-slate-900/60 p-8 shadow-2xl shadow-black/40 backdrop-blur-md"
          noValidate
        >
          {(formError || urlErrorMessage) && (
            <p
              role="alert"
              className="mb-6 rounded-lg border border-red-500/30 bg-red-950/50 px-4 py-3 text-sm text-red-200"
            >
              {formError ?? urlErrorMessage}
            </p>
          )}

          <div className="space-y-5">
            <div className="space-y-2">
              <label
                htmlFor="login-email"
                className="text-sm font-medium text-slate-200"
              >
                Email
              </label>
              <input
                id="login-email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(ev) => {
                  setEmail(ev.target.value);
                  setFieldErrors((f) => {
                    const n = { ...f };
                    delete n.email;
                    return n;
                  });
                }}
                className={`w-full rounded-xl border bg-slate-950/80 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:ring-2 ${
                  fieldErrors.email
                    ? "border-red-500/60 focus:ring-red-500/25"
                    : "border-white/10 focus:border-indigo-500/50 focus:ring-indigo-500/20"
                }`}
                placeholder="you@example.com"
              />
              {fieldErrors.email && (
                <p className="text-sm text-red-400">{fieldErrors.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <label
                htmlFor="login-password"
                className="text-sm font-medium text-slate-200"
              >
                Password
              </label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(ev) => {
                  setPassword(ev.target.value);
                  setFieldErrors((f) => {
                    const n = { ...f };
                    delete n.password;
                    return n;
                  });
                }}
                className={`w-full rounded-xl border bg-slate-950/80 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:ring-2 ${
                  fieldErrors.password
                    ? "border-red-500/60 focus:ring-red-500/25"
                    : "border-white/10 focus:border-indigo-500/50 focus:ring-indigo-500/20"
                }`}
                placeholder="••••••••"
              />
              {fieldErrors.password && (
                <p className="text-sm text-red-400">{fieldErrors.password}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="mt-2 flex w-full justify-center rounded-xl bg-indigo-500 px-4 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-900/30 transition hover:bg-indigo-400 disabled:opacity-50"
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </div>

          <p className="mt-8 text-center text-sm text-slate-400">
            No account?{" "}
            <Link
              href="/signup"
              className="font-semibold text-indigo-400 hover:text-indigo-300 hover:underline"
            >
              Create one
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
