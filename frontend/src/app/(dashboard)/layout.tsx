import { AppShell } from "@/components/layout/AppShell";
import { MembershipGuard } from "@/components/auth/MembershipGuard";
import { SuperAdminRedirect } from "@/components/auth/SuperAdminRedirect";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <MembershipGuard>
      <SuperAdminRedirect />
      <AppShell>{children}</AppShell>
    </MembershipGuard>
  );
}
