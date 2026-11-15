import * as SecureStore from "expo-secure-store";
import { create } from "zustand";

const key = "homefin.householdId";
type HouseholdState = { householdId?: string; setHouseholdId: (id: string) => Promise<void>; hydrate: () => Promise<void> };

export const useHousehold = create<HouseholdState>((set) => ({
  householdId: process.env.EXPO_PUBLIC_HOUSEHOLD_ID,
  async setHouseholdId(id) { await SecureStore.setItemAsync(key, id); set({ householdId: id }); },
  async hydrate() { const id = await SecureStore.getItemAsync(key); if (id) set({ householdId: id }); },
}));
