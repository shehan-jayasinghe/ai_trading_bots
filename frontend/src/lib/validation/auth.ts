import { z, type ZodError } from "zod";

const emailSchema = z
  .string()
  .trim()
  .min(1, "Email is required.")
  .email("Enter a valid email address.")
  .transform((v) => v.toLowerCase());

const signupPasswordSchema = z
  .string()
  .min(1, "Password is required.")
  .min(8, "Password must be at least 8 characters.")
  .max(128, "Password must be 128 characters or fewer.");

const loginPasswordSchema = z.string().min(1, "Password is required.");

export const signupBodySchema = z
  .object({
    email: emailSchema,
    password: signupPasswordSchema,
  })
  .strict();

export const signupFormSchema = z
  .object({
    email: emailSchema,
    password: signupPasswordSchema,
    confirmPassword: z.string().min(1, "Please confirm your password."),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

export const loginFormSchema = z.object({
  email: emailSchema,
  password: loginPasswordSchema,
});

export function zodIssuesToFieldErrors(error: ZodError): Record<string, string> {
  const out: Record<string, string> = {};
  for (const issue of error.issues) {
    const key = issue.path[0];
    if (typeof key === "string" && out[key] === undefined) {
      out[key] = issue.message;
    }
  }
  return out;
}
