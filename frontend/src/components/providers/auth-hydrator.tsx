"use client";

import { useEffect } from "react";

import { useAuthStore } from "@/stores/auth-store";
import { useEstateStore } from "@/stores/estate-store";

export function AuthHydrator() {
  useEffect(() => {
    const unsubscribe = useAuthStore.persist.onFinishHydration(() => {
      if (!useAuthStore.getState().hasRehydrated) {
        useAuthStore.setState({ hasRehydrated: true, isLoading: false });
      }
    });

    void useAuthStore.persist.rehydrate();
    void useEstateStore.persist.rehydrate();

    return unsubscribe;
  }, []);

  return null;
}
