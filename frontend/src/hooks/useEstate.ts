"use client";

import { useQuery } from "@tanstack/react-query";
import { useCallback } from "react";

import { api } from "@/lib/api";
import { useEstateStore } from "@/stores/estate-store";
import type { Estate } from "@/types";

export function useEstate() {
  const {
    currentEstate,
    estates,
    setCurrentEstate,
    setEstates,
    selectEstate,
    clearEstate,
  } = useEstateStore();

  const { isLoading, refetch } = useQuery({
    queryKey: ["estates"],
    queryFn: async () => {
      try {
        const data = await api.getEstates();
        const list = data.results ?? [];
        setEstates(list);
        if (!currentEstate && list.length > 0) {
          setCurrentEstate(list[0]);
        }
        return list;
      } catch {
        return [] as Estate[];
      }
    },
    staleTime: 10 * 60 * 1000,
  });

  const switchEstate = useCallback(
    (estateId: string) => {
      selectEstate(estateId);
    },
    [selectEstate],
  );

  return {
    currentEstate,
    estates,
    isLoading,
    switchEstate,
    setCurrentEstate,
    clearEstate,
    refetchEstates: refetch,
  };
}
