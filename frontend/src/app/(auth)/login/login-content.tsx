"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/toast";
import { useAuth } from "@/hooks/useAuth";
import { resolveLoginDestination } from "@/lib/auth";
import { api, getAccessToken } from "@/lib/api";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/stores/auth-store";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const searchParams = useSearchParams();
  const [mounted, setMounted] = useState(false);
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });
  const {
    login,
    isLoggingIn,
    error,
    clearError,
    isAuthenticated,
    user,
    roles,
    hasActiveMembership,
    isSessionLoading,
    hasRehydrated,
    logout,
  } = useAuth();
  const registered = searchParams.get("registered");
  const redirectTo = searchParams.get("redirect");
  const isPlatformRedirect = redirectTo?.startsWith("/platform");

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!hasRehydrated || isSessionLoading || isLoggingIn || !isAuthenticated || !user) {
      return;
    }
    if (!getAccessToken()) {
      return;
    }
    window.location.replace(
      resolveLoginDestination(
        {
          user,
          roles,
          has_active_membership: hasActiveMembership,
        },
        redirectTo,
      ),
    );
  }, [
    hasActiveMembership,
    hasRehydrated,
    isAuthenticated,
    isLoggingIn,
    isSessionLoading,
    redirectTo,
    roles,
    user,
  ]);

  if (!mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
        <p className="text-sm text-muted-foreground">Loading sign in…</p>
      </div>
    );
  }

  const validatingSavedSession =
    hasRehydrated && isAuthenticated && Boolean(getAccessToken()) && isSessionLoading;

  if (validatingSavedSession) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
        <p className="text-sm text-muted-foreground">Restoring your session…</p>
      </div>
    );
  }

  async function onSubmit(values: LoginFormValues) {
    clearError();
    try {
      await login(values, redirectTo);
      toast.success("Welcome back!");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Invalid email or password";
      toast.error(message);
    }
  }

  async function handleOAuth(provider: "google" | "apple") {
    try {
      sessionStorage.setItem("oauth_provider", provider);
      const { authorization_url } = await api.getOAuthAuthorizeUrl(provider);
      window.location.href = authorization_url;
    } catch {
      toast.error(`${provider === "google" ? "Google" : "Apple"} sign-in is not configured.`);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,hsl(var(--primary)/0.15),transparent_50%)]" />

      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Link href="/" className="inline-flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl gradient-brand text-white font-bold">
              E
            </div>
            <span className="text-xl font-semibold">EstateOS</span>
          </Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">Welcome back</CardTitle>
            <CardDescription>
              {isPlatformRedirect
                ? "Sign in with your super admin account to open the platform console."
                : "Sign in to your estate management dashboard"}
            </CardDescription>
            {registered && (
              <p className="text-sm text-success">
                Account created successfully. Please sign in.
              </p>
            )}
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input
                          type="email"
                          placeholder="you@example.com"
                          autoComplete="email"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Password</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          placeholder="••••••••"
                          autoComplete="current-password"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                {error && (
                  <p className="text-sm text-destructive" role="alert">
                    {error}
                  </p>
                )}
                <Button type="submit" className="w-full" disabled={isLoggingIn}>
                  {isLoggingIn ? "Signing in..." : "Sign in"}
                </Button>
              </form>
            </Form>

            <div className="relative my-6">
              <Separator />
              <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-2 text-xs text-muted-foreground">
                or continue with
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Button type="button" variant="outline" onClick={() => handleOAuth("google")}>
                Google
              </Button>
              <Button type="button" variant="outline" onClick={() => handleOAuth("apple")}>
                Apple
              </Button>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-3">
            <p className="text-sm text-muted-foreground">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="font-medium text-primary hover:underline">
                Register
              </Link>
            </p>
            <p className="text-sm text-muted-foreground">
              Platform administrator?{" "}
              <Link
                href="/login?redirect=/platform"
                className="font-medium text-primary hover:underline"
              >
                Sign in to platform console
              </Link>
            </p>
            {isAuthenticated && user ? (
              <Button
                type="button"
                variant="ghost"
                className="text-sm"
                onClick={() => {
                  logout();
                  useAuthStore.persist.clearStorage();
                  window.location.href = "/login";
                }}
              >
                Clear saved session and sign in again
              </Button>
            ) : null}
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
