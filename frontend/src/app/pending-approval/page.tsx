"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { isPlatformSuperUser } from "@/lib/auth-session";

export default function PendingApprovalPage() {
  const router = useRouter();
  const {
    user,
    roles,
    memberships,
    logout,
    fetchUser,
    isLoading,
    isSessionLoading,
    hasActiveMembership,
  } = useAuth();
  const [checking, setChecking] = useState(false);
  const superAdmin = isPlatformSuperUser(user, roles);
  const loading = isSessionLoading || isLoading;

  useEffect(() => {
    if (loading) return;
    if (superAdmin) {
      router.replace("/platform");
      return;
    }
    if (hasActiveMembership) {
      router.replace("/dashboard");
    }
  }, [hasActiveMembership, loading, router, superAdmin]);

  const pending = (memberships ?? []).filter((membership) => membership.status === "pending");

  async function handleCheckStatus() {
    setChecking(true);
    try {
      const destination = await fetchUser();
      if (destination !== "/pending-approval") {
        router.push(destination);
      }
    } finally {
      setChecking(false);
    }
  }

  if (loading || superAdmin) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
        <Card className="w-full max-w-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Checking your account…</CardTitle>
            <CardDescription>Verifying your access level.</CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl gradient-brand text-lg font-bold text-white">
            E
          </div>
          <CardTitle className="text-2xl">Awaiting estate approval</CardTitle>
          <CardDescription>
            Your registration has been submitted. An estate administrator will review
            your profile and assign your unit before you can access the dashboard.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {pending.map((membership) => (
            <div
              key={membership.resident_profile_id}
              className="rounded-lg border bg-background p-4 text-sm"
            >
              <p className="font-medium">{membership.estate_name}</p>
              <p className="text-muted-foreground">Pending approval</p>
              {membership.unit_number ? (
                <p className="mt-1 text-muted-foreground">Unit: {membership.unit_number}</p>
              ) : null}
            </div>
          ))}

          {user ? (
            <p className="text-center text-sm text-muted-foreground">
              Signed in as {user.email}
            </p>
          ) : null}

          <div className="flex flex-col gap-2 sm:flex-row">
            <Button
              className="flex-1"
              variant="outline"
              onClick={handleCheckStatus}
              disabled={isLoading || checking}
            >
              {checking ? "Checking status..." : "Check approval status"}
            </Button>
            <Button className="flex-1" variant="ghost" onClick={logout}>
              Sign out
            </Button>
          </div>

          <p className="text-center text-xs text-muted-foreground">
            Need help? Contact your estate administrator or{" "}
            <Link href="/" className="text-primary hover:underline">
              return home
            </Link>
            .
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
