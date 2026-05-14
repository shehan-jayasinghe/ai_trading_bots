"use client";

import type { ApiErrorResponse, ApiSuccessResponse } from "@/types";
import {
  signupFormSchema,
  zodIssuesToFieldErrors,
} from "@/lib/validation";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const parsed = signupFormSchema.safeParse({
      email,
      password,
      confirmPassword,
    });
    if (!parsed.success) {
      setFieldErrors(zodIssuesToFieldErrors(parsed.error));
      return;
    }
    setFieldErrors({});

    setLoading(true);
    try {
      const res = await fetch("/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: parsed.data.email,
          password: parsed.data.password,
        }),
      });

      const raw = (await res.json().catch(() => ({}))) as Partial<
        ApiErrorResponse & ApiSuccessResponse
      >;

      if (!res.ok) {
        const err = raw as Partial<ApiErrorResponse>;
        if (err.fieldErrors && Object.keys(err.fieldErrors).length > 0) {
          setFieldErrors(err.fieldErrors);
        }
        if (err.error) setFormError(err.error);
        else if (!err.fieldErrors?.email) {
          setFormError("Something went wrong. Please try again.");
        }
        return;
      }

      router.push("/login");
      router.refresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-full flex-1 bg-slate-950 text-slate-50">
      <div className="relative flex min-h-full flex-col justify-center px-4 py-14">
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
              Create account
            </h1>
            <p className="mt-2 text-sm text-slate-400">
              Email and a strong password
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-white/10 bg-slate-900/60 p-8 shadow-2xl backdrop-blur-md"
            noValidate
          >
            {formError && (
              <p
                role="alert"
                className="mb-6 rounded-lg border border-red-500/30 bg-red-950/50 px-4 py-3 text-sm text-red-200"
              >
                {formError}
              </p>
            )}

            <div className="space-y-5">
              <div className="space-y-2">
                <label
                  htmlFor="signup-email"
                  className="text-sm font-medium text-slate-200"
                >
                  Email
                </label>
                <input
                  id="signup-email"
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
                  className={`w-full rounded-xl border bg-slate-950/80 px-4 py-3 text-sm text-white outline-none focus:ring-2 ${
                    fieldErrors.email
                      ? "border-red-500/60"
                      : "border-white/10 focus:ring-indigo-500/20"
                  }`}
                  placeholder="you@example.com"
                />
                {fieldErrors.email && (
                  <p className="text-sm text-red-400">{fieldErrors.email}</p>
                )}
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="signup-password"
                  className="text-sm font-medium text-slate-200"
                >
                  Password
                </label>
                <input
                  id="signup-password"
                  type="password"
                  autoComplete="new-password"
                  value={password}
                  onChange={(ev) => {
                    setPassword(ev.target.value);
                    setFieldErrors((f) => {
                      const n = { ...f };
                      delete n.password;
                      return n;
                    });
                  }}
                  className={`w-full rounded-xl border bg-slate-950/80 px-4 py-3 text-sm text-white outline-none focus:ring-2 ${
                    fieldErrors.password
                      ? "border-red-500/60"
                      : "border-white/10 focus:ring-indigo-500/20"
                  }`}
                  placeholder="At least 8 characters"
                />
                {fieldErrors.password && (
                  <p className="text-sm text-red-400">{fieldErrors.password}</p>
                )}
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="signup-confirm"
                  className="text-sm font-medium text-slate-200"
                >
                  Confirm password
                </label>
                <input
                  id="signup-confirm"
                  type="password"
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(ev) => {
                    setConfirmPassword(ev.target.value);
                    setFieldErrors((f) => {
                      const n = { ...f };
                      delete n.confirmPassword;
                      return n;
                    });
                  }}
                  className={`w-full rounded-xl border bg-slate-950/80 px-4 py-3 text-sm text-white outline-none focus:ring-2 ${
                    fieldErrors.confirmPassword
                      ? "border-red-500/60"
                      : "border-white/10 focus:ring-indigo-500/20"
                  }`}
                  placeholder="Repeat password"
                />
                {fieldErrors.confirmPassword && (
                  <p className="text-sm text-red-400">
                    {fieldErrors.confirmPassword}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="flex w-full justify-center rounded-xl bg-indigo-500 px-4 py-3.5 text-sm font-semibold text-white shadow-lg transition hover:bg-indigo-400 disabled:opacity-50"
              >
                {loading ? "Creating account…" : "Sign up"}
              </button>
            </div>

            <p className="mt-8 text-center text-sm text-slate-400">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-semibold text-indigo-400 hover:text-indigo-300 hover:underline"
              >
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
