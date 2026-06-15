"use client";

import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";

import { ModulePage } from "@/components/shared/ModulePage";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { MODULE_DESCRIPTIONS, MODULE_ICONS } from "@/lib/navigation";

const data = [
  { name: "Occupancy", value: 94 },
  { name: "Collections", value: 87 },
  { name: "SLA Met", value: 92 },
  { name: "Satisfaction", value: 96 },
];

const chartConfig = {
  value: { label: "Score", color: "hsl(var(--primary))" },
} satisfies ChartConfig;

export default function AnalyticsPage() {
  return (
    <ModulePage
      title="Analytics"
      description={MODULE_DESCRIPTIONS.analytics}
      iconKey="analytics"
      badge="Active"
    >
      <div className="rounded-xl border bg-card p-6">
        <h2 className="mb-4 text-lg font-semibold">Estate Performance</h2>
        <ChartContainer config={chartConfig} className="h-[320px] w-full">
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="value" fill="var(--color-value)" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ChartContainer>
      </div>
    </ModulePage>
  );
}
