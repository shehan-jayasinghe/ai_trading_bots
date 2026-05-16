"use client";

import type { ApiErrorResponse, ApiSuccessResponse } from "@/types";
import { authInputClass, authLabelClass } from "@/lib/auth-form-styles";
import {
  signupFormSchema,
  zodIssuesToFieldErrors,
} from "@/lib/validation";
import Link from "next/link";
import { signIn } from "next-auth/react";
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

      const signInRes = await signIn("credentials", {
        email: parsed.data.email,
        password: parsed.data.password,
        redirect: false,
      });
      if (signInRes?.error) {
        router.push("/login");
        router.refresh();
        return;
      }
      router.push("/");
      router.refresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-full flex-1 bg-white text-slate-900">
      <div className="relative flex min-h-full flex-col justify-center px-4 py-14">
        <div className="relative mx-auto w-full max-w-md">
          <div className="mb-10 text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Deriv AI
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">
              Create account
            </h1>
            <p className="mt-2 text-sm text-slate-600">
              Email and a strong password
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm"
            noValidate
          >
            {formError && (
              <p
                role="alert"
                className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
              >
                {formError}
              </p>
            )}

            <div className="space-y-5">
              <div className="space-y-2">
                <label
                  htmlFor="signup-email"
                  className={authLabelClass}
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
                  className={authInputClass(!!fieldErrors.email)}
                  placeholder="you@example.com"
                />
                {fieldErrors.email && (
                  <p className="text-sm text-red-600">{fieldErrors.email}</p>
                )}
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="signup-password"
                  className={authLabelClass}
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
                  className={authInputClass(!!fieldErrors.password)}
                  placeholder="At least 8 characters"
                />
                {fieldErrors.password && (
                  <p className="text-sm text-red-600">{fieldErrors.password}</p>
                )}
              </div>

              <div className="space-y-2">
                <label
                  htmlFor="signup-confirm"
                  className={authLabelClass}
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
                  className={authInputClass(!!fieldErrors.confirmPassword)}
                  placeholder="Repeat password"
                />
                {fieldErrors.confirmPassword && (
                  <p className="text-sm text-red-600">
                    {fieldErrors.confirmPassword}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="flex w-full justify-center rounded-xl bg-slate-900 px-4 py-3.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50"
              >
                {loading ? "Creating account…" : "Sign up"}
              </button>
            </div>

            <p className="mt-8 text-center text-sm text-slate-600">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-semibold text-slate-900 hover:underline"
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
