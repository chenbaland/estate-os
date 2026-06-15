import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import { setEstateId } from "@/lib/api";
import type { Estate } from "@/types";

interface EstateState {
  currentEstate: Estate | null;
  estates: Estate[];
  isLoading: boolean;
  setCurrentEstate: (estate: Estate | null) => Promise<void>;
  setEstates: (estates: Estate[]) => void;
  selectEstate: (estateId: string) => Promise<void>;
  clearEstate: () => Promise<void>;
}

export const useEstateStore = create<EstateState>()(
  persist(
    (set, get) => ({
      currentEstate: null,
      estates: [],
      isLoading: false,

      setCurrentEstate: async (estate) => {
        await setEstateId(estate?.id ?? null);
        set({ currentEstate: estate });
      },

      setEstates: (estates) => set({ estates }),

      selectEstate: async (estateId) => {
        const estate = get().estates.find((e) => e.id === estateId) ?? null;
        await setEstateId(estate?.id ?? null);
        set({ currentEstate: estate });
      },

      clearEstate: async () => {
        await setEstateId(null);
        set({ currentEstate: null, estates: [] });
      },
    }),
    {
      name: "estateos-estate",
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        currentEstate: state.currentEstate,
        estates: state.estates,
      }),
    },
  ),
);
