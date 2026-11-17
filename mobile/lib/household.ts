import * as SecureStore from "expo-secure-store";
import { create } from "zustand";

const key = "homefin.householdId";
type HouseholdState = { householdId?: string; hydrated: boolean; setHouseholdId: (id: string) => Promise<void>; hydrate: () => Promise<void>; clear: () => Promise<void> };

export const useHousehold = create<HouseholdState>((set) => ({
  householdId: process.env.EXPO_PUBLIC_HOUSEHOLD_ID,
  hydrated: false,
  async setHouseholdId(id) { await SecureStore.setItemAsync(key, id); set({ householdId: id }); },
  async hydrate() { try { const id = await SecureStore.getItemAsync(key); if (id) set({ householdId: id }); } finally { set({ hydrated: true }); } },
  async clear() { await SecureStore.deleteItemAsync(key); set({ householdId: undefined }); },
}));
