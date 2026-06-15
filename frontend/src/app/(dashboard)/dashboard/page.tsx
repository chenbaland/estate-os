"use client";

import {
  CreditCard,
  Package,
  Shield,
  Users,
  Wrench,
} from "lucide-react";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";

import { NotificationPanel } from "@/components/dashboard/NotificationPanel";
import { QuickActions } from "@/components/dashboard/QuickActions";
import { StatCard } from "@/components/dashboard/StatCard";
import { WidgetGrid } from "@/components/dashboard/WidgetGrid";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { useAuth } from "@/hooks/useAuth";
import { getUserDisplayName, ROLE_LABELS } from "@/lib/auth";

const chartData = [
  { month: "Jan", visitors: 186, revenue: 4200 },
  { month: "Feb", visitors: 205, revenue: 4800 },
  { month: "Mar", visitors: 237, revenue: 5100 },
  { month: "Apr", visitors: 273, revenue: 5400 },
  { month: "May", visitors: 209, revenue: 4900 },
  { month: "Jun", visitors: 314, revenue: 6200 },
];

const chartConfig = {
  visitors: { label: "Visitors", color: "hsl(var(--primary))" },
  revenue: { label: "Revenue", color: "hsl(var(--info))" },
} satisfies ChartConfig;

export default function DashboardPage() {
  const { user, roles } = useAuth();
  const primaryRole = roles[0]?.code;
  const roleLabel = primaryRole ? ROLE_LABELS[primaryRole] : "Resident";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
          Good {getGreeting()}, {getUserDisplayName(user).split(" ")[0]}
        </h1>
        <p className="text-muted-foreground">
          {roleLabel} dashboard — here&apos;s what&apos;s happening in your estate today.
        </p>
      </div>

      <WidgetGrid>
        <StatCard
          label="Active Residents"
          value="1,248"
          change={4.2}
          trend="up"
          icon={<Users className="h-4 w-4" />}
          index={0}
        />
        <StatCard
          label="Visitors Today"
          value="47"
          change={12}
          trend="up"
          icon={<Shield className="h-4 w-4" />}
          index={1}
        />
        <StatCard
          label="Open Tickets"
          value="23"
          change={-8}
          trend="down"
          icon={<Wrench className="h-4 w-4" />}
          index={2}
        />
        <StatCard
          label="Pending Invoices"
          value="₦2.4M"
          change={2.1}
          trend="up"
          icon={<CreditCard className="h-4 w-4" />}
          index={3}
        />
      </WidgetGrid>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <QuickActions />
          <div className="rounded-xl border bg-card p-6">
            <h2 className="mb-4 text-lg font-semibold">Estate Activity</h2>
            <ChartContainer config={chartConfig} className="h-[280px] w-full">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="month"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={8}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Area
                  type="monotone"
                  dataKey="visitors"
                  stroke="var(--color-visitors)"
                  fill="var(--color-visitors)"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
              </AreaChart>
            </ChartContainer>
          </div>
        </div>
        <NotificationPanel />
      </div>

      <div className="rounded-xl border bg-muted/30 p-6">
        <div className="flex items-center gap-3">
          <Package className="h-5 w-5 text-primary" />
          <div>
            <p className="font-medium">Role-based view</p>
            <p className="text-sm text-muted-foreground">
              Navigation and widgets adapt to your role ({roleLabel}). Admins see
              analytics and security modules; residents see billing and community tools.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "morning";
  if (hour < 17) return "afternoon";
  return "evening";
}
