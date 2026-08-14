import { UserButton } from "@clerk/nextjs";
import { Dashboard } from "@/components/Dashboard";
import { config } from "@/lib/config";

export default function DashboardPage() {
  return (
    <main className="page-shell">
      {config.clerkEnabled && (
        <div className="user-menu">
          <UserButton afterSignOutUrl="/" />
        </div>
      )}
      <Dashboard />
    </main>
  );
}
