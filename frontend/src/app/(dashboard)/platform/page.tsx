"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2, Clock3, Shield, Users } from "lucide-react";
import Link from "next/link";

import { StatCard } from "@/components/dashboard/StatCard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function PlatformOverviewPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["platform-overview"],
    queryFn: () => api.getPlatformOverview(),
  });

  return (
    <div className="space-y-6">
      <p className="text-muted-foreground">
        Manage estates, assign administrators, and monitor platform-wide onboarding activity.
      </p>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard
          label="Total Estates"
          value={isLoading ? "..." : String(data?.estates_total ?? 0)}
          icon={<Building2 className="h-4 w-4" />}
          index={0}
        />
        <StatCard
          label="Active Estates"
          value={isLoading ? "..." : String(data?.estates_active ?? 0)}
          icon={<Building2 className="h-4 w-4" />}
          index={1}
        />
        <StatCard
          label="Platform Users"
          value={isLoading ? "..." : String(data?.users_total ?? 0)}
          icon={<Users className="h-4 w-4" />}
          index={2}
        />
        <StatCard
          label="Estate Admins"
          value={isLoading ? "..." : String(data?.estate_admins_total ?? 0)}
          icon={<Shield className="h-4 w-4" />}
          index={3}
        />
        <StatCard
          label="Pending Registrations"
          value={isLoading ? "..." : String(data?.pending_registrations ?? 0)}
          icon={<Clock3 className="h-4 w-4" />}
          index={4}
        />
        <StatCard
          label="Total Units"
          value={isLoading ? "..." : String(data?.units_total ?? 0)}
          icon={<Building2 className="h-4 w-4" />}
          index={5}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick actions</CardTitle>
            <CardDescription>Common super admin workflows</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3 sm:flex-row">
            <Button asChild>
              <Link href="/platform/estates?create=true">Create estate</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/platform/admins">Assign estate admin</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Platform responsibilities</CardTitle>
            <CardDescription>What super admins manage in EstateOS</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>Provision new estates and seed default roles automatically.</p>
            <p>Assign or revoke estate administrators and operational admins.</p>
            <p>Monitor pending resident registrations across all estates.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
