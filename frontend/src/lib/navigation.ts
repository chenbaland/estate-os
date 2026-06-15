import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BarChart3,
  Bot,
  Building2,
  Car,
  CreditCard,
  HeartPulse,
  Home,
  LayoutDashboard,
  Package,
  Pill,
  ScrollText,
  Settings,
  Shield,
  ShoppingBag,
  Sparkles,
  Stethoscope,
  Truck,
  UserCog,
  Users,
  Wrench,
  Zap,
} from "lucide-react";

import type { RoleCode, User } from "@/types";

export interface NavItemConfig {
  title: string;
  href: string;
  icon: LucideIcon;
  roles?: RoleCode[];
  group?: string;
}

export const NAV_ITEMS: NavItemConfig[] = [
  { title: "Dashboard", href: "/dashboard", icon: Home, group: "Overview" },
  { title: "Residents", href: "/residents", icon: Users, group: "People", roles: ["super_admin", "estate_admin", "finance_admin"] },
  { title: "Visitors", href: "/visitors", icon: Users, group: "People" },
  {
    title: "Security",
    href: "/security",
    icon: Shield,
    group: "Operations",
    roles: ["super_admin", "estate_admin", "security_admin", "security_personnel"],
  },
  {
    title: "Billing",
    href: "/billing",
    icon: CreditCard,
    group: "Finance",
    roles: ["super_admin", "estate_admin", "finance_admin", "resident"],
  },
  { title: "Utilities", href: "/utilities", icon: Zap, group: "Finance" },
  { title: "Marketplace", href: "/marketplace", icon: ShoppingBag, group: "Services" },
  { title: "Pharmacy", href: "/pharmacy", icon: Pill, group: "Health" },
  { title: "Healthcare", href: "/healthcare", icon: Stethoscope, group: "Health" },
  { title: "Facilities", href: "/facilities", icon: Building2, group: "Operations" },
  { title: "Maintenance", href: "/maintenance", icon: Wrench, group: "Operations" },
  { title: "Packages", href: "/packages", icon: Package, group: "Operations" },
  { title: "Parking", href: "/parking", icon: Car, group: "Operations" },
  { title: "Community", href: "/community", icon: Sparkles, group: "Community" },
  { title: "Transportation", href: "/transportation", icon: Truck, group: "Services" },
  {
    title: "Analytics",
    href: "/analytics",
    icon: BarChart3,
    group: "Insights",
    roles: ["super_admin", "estate_admin", "finance_admin"],
  },
  { title: "AI Concierge", href: "/ai-concierge", icon: Bot, group: "Insights" },
  { title: "Settings", href: "/settings", icon: Settings, group: "System" },
];

export const PLATFORM_NAV_ITEMS: NavItemConfig[] = [
  { title: "Platform Overview", href: "/platform", icon: LayoutDashboard, group: "Platform" },
  { title: "Estates", href: "/platform/estates", icon: Building2, group: "Platform" },
  { title: "Estate Admins", href: "/platform/admins", icon: UserCog, group: "Platform" },
  { title: "Audit Logs", href: "/platform/audit-logs", icon: ScrollText, group: "Platform" },
  { title: "Analytics", href: "/analytics", icon: BarChart3, group: "Insights" },
  { title: "Settings", href: "/settings", icon: Settings, group: "System" },
];

export const NAV_GROUPS = [
  "Platform",
  "Overview",
  "People",
  "Operations",
  "Finance",
  "Services",
  "Health",
  "Community",
  "Insights",
  "System",
] as const;

export function getNavItemsForRoles(
  roles: RoleCode[] | undefined | null,
  user?: User | null,
  pathname?: string,
): NavItemConfig[] {
  const safeRoles = roles ?? [];
  const platformContext =
    pathname?.startsWith("/platform") ||
    safeRoles.includes("super_admin") ||
    Boolean(user?.is_superuser);

  if (platformContext) {
    return PLATFORM_NAV_ITEMS;
  }

  if (safeRoles.length === 0) return NAV_ITEMS;
  const isAdmin = safeRoles.some((r) =>
    ["estate_admin"].includes(r),
  );
  if (isAdmin) return NAV_ITEMS;

  return NAV_ITEMS.filter(
    (item) => !item.roles || item.roles.some((role) => safeRoles.includes(role)),
  );
}

export const MODULE_DESCRIPTIONS: Record<string, string> = {
  residents: "Manage resident profiles, family members, and vehicles.",
  visitors: "Issue visitor passes and track entry logs.",
  security: "Monitor incidents, patrols, and emergency alerts.",
  billing: "Invoices, payments, and fee management.",
  utilities: "Utility accounts, consumption, and token purchases.",
  marketplace: "Vendor marketplace for estate services and products.",
  pharmacy: "Prescriptions, medication orders, and reminders.",
  healthcare: "Hospital appointments, ambulance, and medical records.",
  facilities: "Book amenities and manage facility schedules.",
  maintenance: "Submit and track maintenance tickets.",
  packages: "Track incoming and outgoing deliveries.",
  parking: "Parking slots, permits, and EV charging.",
  community: "Announcements, polls, and community groups.",
  transportation: "Ride requests and estate shuttle services.",
  analytics: "Estate-wide metrics and performance dashboards.",
  "ai-concierge": "AI-powered assistant for residents and staff.",
  settings: "Account preferences and estate configuration.",
};

export const MODULE_ICONS: Record<string, LucideIcon> = {
  residents: Users,
  visitors: Users,
  security: Shield,
  billing: CreditCard,
  utilities: Zap,
  marketplace: ShoppingBag,
  pharmacy: Pill,
  healthcare: HeartPulse,
  facilities: Building2,
  maintenance: Wrench,
  packages: Package,
  parking: Car,
  community: Sparkles,
  transportation: Truck,
  analytics: BarChart3,
  "ai-concierge": Bot,
  settings: Settings,
  dashboard: Activity,
};
