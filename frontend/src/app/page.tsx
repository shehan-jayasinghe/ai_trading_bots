import { auth } from "@/auth";
import { SignOutButton } from "@/components/sign-out-button";
import { redirect } from "next/navigation";

export default async function Home() {
  const session = await auth();
  if (!session?.user) {
    redirect("/login");
  }

  return (
    <div className="flex min-h-full flex-1 flex-col text-slate-50">
      <header className="border-b border-white/10 bg-slate-900/80 px-6 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <span className="text-sm font-semibold uppercase tracking-widest text-indigo-400/90">
            Deriv AI
          </span>
          <SignOutButton />
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-12">
        <h1 className="text-2xl font-semibold text-white">
          Welcome
          {session.user?.email ? (
            <span className="text-slate-400"> — {session.user.email}</span>
          ) : null}
        </h1>
        <p className="mt-4 max-w-xl text-slate-400">
          You are signed in. Build your workflows and tools from here.
        </p>
      </main>
    </div>
  );
}
