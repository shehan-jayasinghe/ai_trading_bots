import { auth } from "@/auth";
import { SignOutButton } from "@/components/sign-out-button";
import { WorkflowsDashboard } from "@/components/workflows/workflows-dashboard";
import { redirect } from "next/navigation";

export default async function Home() {
  const session = await auth();
  if (!session?.user) {
    redirect("/login");
  }

  return (
    <div className="flex min-h-full flex-1 flex-col bg-white text-slate-900">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <span className="text-sm font-semibold uppercase tracking-widest text-slate-600">
            Deriv AI
          </span>
          <SignOutButton />
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-12">
        <h1 className="text-2xl font-semibold text-slate-900">
          Welcome
          {session.user?.email ? (
            <span className="text-slate-500"> — {session.user.email}</span>
          ) : null}
        </h1>
        <p className="mt-2 text-slate-600">
          Manage your trading workflows below.
        </p>
        <WorkflowsDashboard />
      </main>
    </div>
  );
}
