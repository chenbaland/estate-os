"use client";

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { MODULE_ICONS } from "@/lib/navigation";

interface ModulePageProps {
  title: string;
  description: string;
  iconKey: keyof typeof MODULE_ICONS;
  badge?: string;
  children?: React.ReactNode;
}

export function ModulePage({
  title,
  description,
  iconKey,
  badge = "Coming soon",
  children,
}: ModulePageProps) {
  const Icon: LucideIcon = MODULE_ICONS[iconKey];
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-4">
          <div className="rounded-xl gradient-brand p-3 text-white shadow-lg">
            <Icon className="h-6 w-6" aria-hidden />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">{title}</h1>
              <Badge variant="secondary">{badge}</Badge>
            </div>
            <p className="mt-1 max-w-2xl text-muted-foreground">{description}</p>
          </div>
        </div>
      </div>

      {children ?? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-3 w-full" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-24 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </motion.div>
  );
}

export function ModulePlaceholder({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>
          This module connects to the EstateOS backend API. Data will populate once
          endpoints are available.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2 text-sm text-muted-foreground">
          {items.map((item) => (
            <li key={item} className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              {item}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
