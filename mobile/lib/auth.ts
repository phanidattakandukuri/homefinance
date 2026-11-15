import { create } from "zustand";
import { api, clearTokens, persistTokens, restoreTokens, TokenPair, User } from "./api";

type AuthState = {
  user?: User;
  tokens?: TokenPair;
  hydrated: boolean;
  loading: boolean;
  error?: string;
  login: (email: string, password: string) => Promise<void>;
  hydrate: () => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
};

export const useAuth = create<AuthState>((set) => ({
  hydrated: false,
  loading: false,
  async hydrate() {
    try {
      const tokens = await restoreTokens();
      if (!tokens) return;
      const user = await api.me();
      set({ tokens, user });
    } catch {
      await clearTokens();
    } finally {
      set({ hydrated: true });
    }
  },
  async login(email, password) {
    set({ loading: true, error: undefined });
    try {
      const tokens = await api.login({ email, password });
      await persistTokens(tokens);
      const user = await api.me();
      set({ tokens, user });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : "Unable to log in." });
      throw error;
    } finally {
      set({ loading: false });
    }
  },
  async logout() {
    await clearTokens();
    set({ tokens: undefined, user: undefined, error: undefined });
  },
  clearError: () => set({ error: undefined }),
}));
