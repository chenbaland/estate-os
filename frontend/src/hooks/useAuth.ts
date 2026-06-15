"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { usePathname, useRouter } from "next/navigation";
import { useCallback } from "react";

import { api } from "@/lib/api";
import { resolveLoginDestination } from "@/lib/auth";
import { isPlatformSuperUser } from "@/lib/auth-session";
import { useAuthStore } from "@/stores/auth-store";
import type { LoginCredentials, RegisterPayload } from "@/types";

export function useAuth() {
  const router = useRouter();
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const {
    user,
    roles,
    memberships,
    hasActiveMembership,
    pendingMembership,
    isAuthenticated,
    isLoading,
    error,
    login: storeLogin,
    logout,
    fetchUser,
    clearError,
    applySession,
    setTokens,
    hasRehydrated,
  } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: ({
      credentials,
      redirectPath,
    }: {
      credentials: LoginCredentials;
      redirectPath?: string | null;
    }) => storeLogin(credentials, redirectPath),
    onSuccess: (destination) => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      window.location.assign(destination);
    },
  });

  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => api.register(payload),
    onSuccess: async (result) => {
      setTokens({ access: result.access, refresh: result.refresh });
      const session = await api.getCurrentUser();
      applySession(session);
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      const destination = resolveLoginDestination(session);
      window.location.assign(destination);
    },
  });

  const { refetch: refetchUser, isFetching } = useQuery({
    queryKey: ["currentUser"],
    queryFn: async () => {
      await fetchUser();
      const state = useAuthStore.getState();
      const onAuthPage =
        pathname === "/login" ||
        pathname === "/register" ||
        pathname.startsWith("/auth/");

      if (onAuthPage) {
        return state.user ?? null;
      }

      if (isPlatformSuperUser(state.user, state.roles)) {
        router.replace("/platform");
        return state.user ?? null;
      }
      if (!state.hasActiveMembership && state.pendingMembership) {
        router.replace("/pending-approval");
      }
      return state.user ?? null;
    },
    enabled: isAuthenticated && hasRehydrated,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });

  const isSessionLoading = isAuthenticated && hasRehydrated && (isLoading || isFetching);

  const handleLogin = useCallback(
    async (credentials: LoginCredentials, redirectPath?: string | null) => {
      await loginMutation.mutateAsync({ credentials, redirectPath });
    },
    [loginMutation],
  );

  const handleRegister = useCallback(
    async (payload: RegisterPayload) => {
      await registerMutation.mutateAsync(payload);
    },
    [registerMutation],
  );

  return {
    user,
    roles,
    memberships,
    hasActiveMembership,
    pendingMembership,
    isAuthenticated,
    isLoading: isLoading || loginMutation.isPending || isFetching,
    isSessionLoading,
    error: error ?? loginMutation.error?.message ?? registerMutation.error?.message,
    login: handleLogin,
    register: handleRegister,
    logout,
    fetchUser,
    refetchUser,
    clearError,
    isRegistering: registerMutation.isPending,
    isLoggingIn: loginMutation.isPending,
    hasRehydrated,
  };
}
