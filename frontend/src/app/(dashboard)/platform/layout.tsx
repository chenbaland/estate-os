"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { PlatformGuard } from "@/components/platform/PlatformGuard";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const PLATFORM_LINKS = [
  { href: "/platform", label: "Overview" },
  { href: "/platform/estates", label: "Estates" },
  { href: "/platform/admins", label: "Estate Admins" },
  { href: "/platform/audit-logs", label: "Audit Logs" },
];

export default function PlatformLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <PlatformGuard>
      <div className="space-y-6">
        <div className="flex flex-col gap-4 border-b pb-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-medium text-primary">Platform Administration</p>
            <h1 className="text-2xl font-bold tracking-tight">Super Admin Console</h1>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <nav className="flex flex-wrap gap-2">
              {PLATFORM_LINKS.map((link) => {
                const active =
                  pathname === link.href ||
                  (link.href !== "/platform" && pathname.startsWith(link.href));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={cn(
                      "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      active
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground hover:text-foreground",
                    )}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </nav>
            <Button asChild className="shrink-0">
              <Link href="/platform/estates?create=true">Create estate</Link>
            </Button>
          </div>
        </div>
        {children}
      </div>
    </PlatformGuard>
  );
}
