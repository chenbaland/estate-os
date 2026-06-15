"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, setTokens } from "@/lib/api";
import { resolveLoginDestination } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";

export default function OAuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const fetchUser = useAuthStore((s) => s.fetchUser);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");
    const idToken = searchParams.get("id_token");
    const provider = (sessionStorage.getItem("oauth_provider") ?? "google") as "google" | "apple";

    if (!code && !idToken) {
      setError("Missing OAuth credentials.");
      return;
    }

    (async () => {
      try {
        const result = await api.oauthCallback(provider, {
          code: code ?? undefined,
          id_token: idToken ?? undefined,
          identity_token: idToken ?? undefined,
        });
        setTokens({ access: result.access, refresh: result.refresh });
        await fetchUser();
        const state = useAuthStore.getState();
        if (state.user) {
          router.replace(
            resolveLoginDestination({
              user: state.user,
              roles: state.roles,
              has_active_membership: state.hasActiveMembership,
            }),
          );
        } else {
          router.replace("/login");
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "OAuth sign-in failed.");
      }
    })();
  }, [searchParams, fetchUser, router]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Completing sign in…</CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <>
              <p className="mb-4 text-sm text-destructive">{error}</p>
              <Button onClick={() => router.push("/login")}>Back to login</Button>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Please wait while we verify your account.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
