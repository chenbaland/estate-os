"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/hooks/useAuth";
import { useHydrated } from "@/hooks/useHydrated";
import { isSuperAdmin } from "@/lib/auth";
import { getNavItemsForRoles, NAV_GROUPS, NAV_ITEMS, PLATFORM_NAV_ITEMS } from "@/lib/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { cn, getInitials } from "@/lib/utils";

interface SidebarProps {
  className?: string;
  onNavigate?: () => void;
}

export function Sidebar({ className, onNavigate }: SidebarProps) {
  const pathname = usePathname();
  const hydrated = useHydrated();
  const hasRehydrated = useAuthStore((state) => state.hasRehydrated);
  const { user, roles } = useAuth();
  const roleCodes = (roles ?? []).map((r) => r.code);
  const authReady = hydrated && hasRehydrated;

  const navItems = authReady
    ? getNavItemsForRoles(roleCodes, user, pathname)
    : pathname.startsWith("/platform")
      ? PLATFORM_NAV_ITEMS
      : NAV_ITEMS;

  const platformMode =
    pathname.startsWith("/platform") ||
    (authReady && isSuperAdmin(roles, user));

  const primaryRoleLabel = platformMode ? "Super Admin" : roles[0]?.name;

  return (
    <aside
      className={cn(
        "flex h-full w-[var(--sidebar-width)] flex-col border-r bg-card",
        className,
      )}
    >
      <div className="flex h-[var(--header-height)] items-center gap-2 border-b px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg gradient-brand text-white font-bold text-sm">
          E
        </div>
        <div>
          <p className="font-semibold tracking-tight">EstateOS</p>
          <p className="text-xs text-muted-foreground" suppressHydrationWarning>
            {platformMode ? "Platform Admin" : "Smart Living"}
          </p>
        </div>
      </div>

      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-6" aria-label="Main navigation">
          {NAV_GROUPS.map((group) => {
            const items = navItems.filter((item) => item.group === group);
            if (items.length === 0) return null;

            return (
              <div key={group}>
                <p className="mb-2 px-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  {group}
                </p>
                <ul className="space-y-1">
                  {items.map((item) => {
                    const isActive =
                      pathname === item.href ||
                      pathname.startsWith(`${item.href}/`);
                    const Icon = item.icon;

                    return (
                      <li key={item.href}>
                        <Link
                          href={item.href}
                          onClick={onNavigate}
                          className={cn(
                            "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                            isActive
                              ? "bg-primary text-primary-foreground shadow-sm"
                              : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                          )}
                          aria-current={isActive ? "page" : undefined}
                        >
                          <Icon className="h-4 w-4 shrink-0" aria-hidden />
                          {item.title}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            );
          })}
        </nav>
      </ScrollArea>

      {authReady && user && (
        <>
          <Separator />
          <div className="flex items-center gap-3 p-4">
            <Avatar className="h-9 w-9">
              <AvatarImage src={user.avatar ?? undefined} alt="" />
              <AvatarFallback>
                {getInitials(user.first_name, user.last_name)}
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {user.first_name} {user.last_name}
              </p>
              <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            </div>
            {primaryRoleLabel && (
              <Badge variant="secondary" className="shrink-0 text-[10px]">
                {primaryRoleLabel}
              </Badge>
            )}
          </div>
        </>
      )}
    </aside>
  );
}
