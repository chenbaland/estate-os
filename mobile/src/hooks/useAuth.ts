import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as LocalAuthentication from "expo-local-authentication";
import { useRouter } from "expo-router";
import { useCallback } from "react";

import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type { LoginCredentials, RegisterPayload } from "@/types";

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const {
    user,
    roles,
    isAuthenticated,
    isLoading,
    error,
    biometricEnabled,
    login: storeLogin,
    logout,
    fetchUser,
    clearError,
    setBiometricEnabled,
  } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => storeLogin(credentials),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] });
      router.replace("/(tabs)");
    },
  });

  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => api.register(payload),
    onSuccess: () => {
      router.replace("/(auth)/login");
    },
  });

  const { refetch: refetchUser, isFetching } = useQuery({
    queryKey: ["currentUser"],
    queryFn: () => api.getCurrentUser(),
    enabled: isAuthenticated && !user,
    staleTime: 5 * 60 * 1000,
  });

  const handleLogin = useCallback(
    async (credentials: LoginCredentials) => {
      await loginMutation.mutateAsync(credentials);
    },
    [loginMutation],
  );

  const handleRegister = useCallback(
    async (payload: RegisterPayload) => {
      await registerMutation.mutateAsync(payload);
    },
    [registerMutation],
  );

  const handleLogout = useCallback(async () => {
    await logout();
    queryClient.clear();
    router.replace("/(auth)/login");
  }, [logout, queryClient, router]);

  const checkBiometricSupport = useCallback(async () => {
    const compatible = await LocalAuthentication.hasHardwareAsync();
    const enrolled = await LocalAuthentication.isEnrolledAsync();
    return compatible && enrolled;
  }, []);

  const authenticateWithBiometrics = useCallback(async (): Promise<boolean> => {
    const supported = await checkBiometricSupport();
    if (!supported) return false;

    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: "Unlock EstateOS",
      cancelLabel: "Use password",
      disableDeviceFallback: false,
      fallbackLabel: "Enter passcode",
    });

    return result.success;
  }, [checkBiometricSupport]);

  const enableBiometric = useCallback(async () => {
    const supported = await checkBiometricSupport();
    if (!supported) {
      throw new Error("Biometric authentication is not available on this device.");
    }

    const authenticated = await authenticateWithBiometrics();
    if (!authenticated) {
      throw new Error("Biometric authentication failed.");
    }

    setBiometricEnabled(true);
  }, [authenticateWithBiometrics, checkBiometricSupport, setBiometricEnabled]);

  const disableBiometric = useCallback(() => {
    setBiometricEnabled(false);
  }, [setBiometricEnabled]);

  return {
    user,
    roles,
    isAuthenticated,
    isLoading: isLoading || loginMutation.isPending || isFetching,
    error:
      error ??
      loginMutation.error?.message ??
      registerMutation.error?.message,
    biometricEnabled,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    fetchUser,
    refetchUser,
    clearError,
    checkBiometricSupport,
    authenticateWithBiometrics,
    enableBiometric,
    disableBiometric,
    isRegistering: registerMutation.isPending,
    isLoggingIn: loginMutation.isPending,
  };
}
