import { SignIn } from "@clerk/nextjs";
import { config } from "@/lib/config";
import { redirect } from "next/navigation";

export default function SignInPage() {
  if (!config.clerkEnabled) {
    redirect("/dashboard");
  }

  return (
    <main className="auth-page">
      <SignIn />
    </main>
  );
}
