"use client";

import { motion } from "framer-motion";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { DashboardStat } from "@/types";

interface StatCardProps extends DashboardStat {
  icon?: React.ReactNode;
  index?: number;
}

export function StatCard({
  label,
  value,
  change,
  trend = "neutral",
  icon,
  index = 0,
}: StatCardProps) {
  const TrendIcon =
    trend === "up" ? ArrowUpRight : trend === "down" ? ArrowDownRight : Minus;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05 }}
    >
      <Card className="overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {label}
          </CardTitle>
          {icon && (
            <div className="rounded-lg bg-primary/10 p-2 text-primary">{icon}</div>
          )}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold tracking-tight">{value}</div>
          {change !== undefined && (
            <p
              className={cn(
                "mt-1 flex items-center gap-1 text-xs",
                trend === "up" && "text-success",
                trend === "down" && "text-destructive",
                trend === "neutral" && "text-muted-foreground",
              )}
            >
              <TrendIcon className="h-3 w-3" />
              {change > 0 ? "+" : ""}
              {change}% from last month
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
