import { create } from "zustand";
import { persist } from "zustand/middleware";

import { setEstateId } from "@/lib/api";
import type { Estate } from "@/types";

interface EstateState {
  currentEstate: Estate | null;
  estates: Estate[];
  isLoading: boolean;
  setCurrentEstate: (estate: Estate | null) => void;
  setEstates: (estates: Estate[]) => void;
  selectEstate: (estateId: string) => void;
  clearEstate: () => void;
}

export const useEstateStore = create<EstateState>()(
  persist(
    (set, get) => ({
      currentEstate: null,
      estates: [],
      isLoading: false,

      setCurrentEstate: (estate) => {
        setEstateId(estate?.id ?? null);
        set({ currentEstate: estate });
      },

      setEstates: (estates) => set({ estates }),

      selectEstate: (estateId) => {
        const estate = get().estates.find((e) => e.id === estateId) ?? null;
        setEstateId(estate?.id ?? null);
        set({ currentEstate: estate });
      },

      clearEstate: () => {
        setEstateId(null);
        set({ currentEstate: null, estates: [] });
      },
    }),
    {
      name: "estateos-estate",
      skipHydration: true,
      partialize: (state) => ({
        currentEstate: state.currentEstate,
        estates: state.estates,
      }),
      onRehydrateStorage: () => (state) => {
        if (state?.currentEstate?.id) {
          setEstateId(state.currentEstate.id);
        }
      },
    },
  ),
);
