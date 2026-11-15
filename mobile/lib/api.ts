import * as SecureStore from "expo-secure-store";

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer" | string;
};

export type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
};

export type Member = {
  id: string;
  user_id: string | null;
  display_name: string;
  role: string;
  membership_status: string;
};

export type Household = {
  id: string;
  name: string;
  base_currency: string;
  timezone: string;
  members: Member[];
};

export type Dashboard = {
  period_start: string;
  period_end: string;
  total_income: number | string;
  total_expenses: number | string;
  monthly_savings: number | string;
  savings_rate: number | string | null;
  total_investments: number | string;
  total_assets: number | string;
  total_liabilities: number | string;
  net_worth: number | string;
  monthly_cash_flow: number | string;
  expense_categories: Record<string, number | string>;
  member_totals: Record<string, { income: number | string; expenses: number | string }>;
  investment_allocation: Record<string, number | string>;
  pf_overview: Record<string, number | string>;
};

export type Transaction = {
  id: string;
  household_id: string;
  member_id: string;
  account_id: string | null;
  transaction_type: string;
  category_id: string;
  amount: number | string;
  currency: string;
  transaction_date: string;
  description: string | null;
  merchant: string | null;
  payment_method: string | null;
  notes: string | null;
  source: string | null;
  reference_number: string | null;
  linked_transaction_id: string | null;
  is_void: boolean;
};

export type Category = { id: string; name: string; parent_id: string | null };
export type RegisterPayload = { full_name: string; email: string; password: string };
export type HouseholdPayload = {
  name: string;
  base_currency: string;
  timezone: string;
  earning_member_names: string[];
};
export type TransactionPayload = {
  member_id: string;
  category_id: string;
  transaction_type: string;
  amount: string;
  currency: string;
  transaction_date: string;
  description?: string;
  merchant?: string;
  payment_method?: string;
};

const baseUrl = (process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");
let accessToken: string | undefined;
let refreshToken: string | undefined;

export const tokenStorageKey = "homefin.tokens";

export async function restoreTokens(): Promise<TokenPair | undefined> {
  const raw = await SecureStore.getItemAsync(tokenStorageKey);
  if (!raw) return undefined;
  try {
    const tokens = JSON.parse(raw) as TokenPair;
    setTokens(tokens);
    return tokens;
  } catch {
    await SecureStore.deleteItemAsync(tokenStorageKey);
    return undefined;
  }
}

export function setTokens(tokens?: TokenPair): void {
  accessToken = tokens?.access_token;
  refreshToken = tokens?.refresh_token;
}

export async function persistTokens(tokens: TokenPair): Promise<void> {
  setTokens(tokens);
  await SecureStore.setItemAsync(tokenStorageKey, JSON.stringify(tokens));
}

export async function clearTokens(): Promise<void> {
  setTokens(undefined);
  await SecureStore.deleteItemAsync(tokenStorageKey);
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string | { msg?: string }[] };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) return body.detail.map((item) => item.msg ?? "Invalid value").join(", ");
  } catch {
    // Keep a useful generic message when a server returns a non-JSON error.
  }
  return `Request failed (${response.status})`;
}

async function rawRequest<T>(path: string, options: RequestInit = {}, token?: string, idempotencyKey?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (idempotencyKey) headers.set("X-Idempotency-Key", idempotencyKey);
  const response = await fetch(`${baseUrl}${path}`, { ...options, headers });
  if (!response.ok) throw new ApiError(response.status, await parseError(response));
  return response.status === 204 ? (undefined as T) : (await response.json()) as T;
}

async function request<T>(path: string, options: RequestInit = {}, retry = true, idempotencyKey?: string): Promise<T> {
  try {
    return await rawRequest<T>(path, options, accessToken, idempotencyKey);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401 && retry && refreshToken) {
      const tokens = await rawRequest<TokenPair>(`/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`, { method: "POST" });
      await persistTokens(tokens);
      return request<T>(path, options, false);
    }
    throw error;
  }
}

export const api = {
  register: (body: RegisterPayload) => request<User>("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body: { email: string; password: string }) => request<TokenPair>("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  me: () => request<User>("/auth/me"),
  createHousehold: (body: HouseholdPayload) => request<Household>("/households", { method: "POST", body: JSON.stringify(body) }),
  household: (id: string) => request<Household>(`/households/${id}`),
  members: (id: string) => request<Member[]>(`/households/${id}/members`),
  dashboard: (id: string) => request<Dashboard>(`/households/${id}/analytics/household`),
  categories: (id: string) => request<Category[]>(`/households/${id}/categories`),
  transactions: (id: string, search = "") =>
    request<Transaction[]>(`/households/${id}/transactions${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  createTransaction: (id: string, body: TransactionPayload, idempotencyKey?: string) =>
    request<Transaction>(`/households/${id}/transactions`, { method: "POST", body: JSON.stringify(body) }, true, idempotencyKey),
  investments: (id: string) => request<unknown[]>(`/households/${id}/wealth/investments`),
  assets: (id: string) => request<unknown[]>(`/households/${id}/wealth/assets`),
  liabilities: (id: string) => request<unknown[]>(`/households/${id}/wealth/liabilities`),
  investmentTransactions: (id: string, investmentId: string, body: unknown) => request<unknown>(`/households/${id}/wealth/investments/${investmentId}/transactions`, { method: "POST", body: JSON.stringify(body) }),
  salary: (id: string, memberId: string) => request<unknown[]>(`/households/${id}/members/${memberId}/salary`),
  createSalary: (id: string, memberId: string, body: unknown) => request<unknown>(`/households/${id}/members/${memberId}/salary`, { method: "POST", body: JSON.stringify(body) }),
  snapshots: (id: string) => request<unknown[]>(`/households/${id}/analytics/snapshots`),
  extraction: (id: string, documentId: string) => request<any>(`/households/${id}/documents/${documentId}/extraction`),
  confirmExtraction: (id: string, documentId: string, body: unknown) => request<any>(`/households/${id}/documents/${documentId}/confirm`, { method: "POST", body: JSON.stringify(body) }),
  updateMember: (id: string, memberId: string, body: unknown) => request<Member>(`/households/${id}/members/${memberId}`, { method: "PATCH", body: JSON.stringify(body) }),
  removeMember: (id: string, memberId: string) => request<void>(`/households/${id}/members/${memberId}`, { method: "DELETE" }),
  askAssistant: (id: string, question: string) => request<{answer:string;evidence:unknown[]}>(`/households/${id}/assistant/ask`, { method: "POST", body: JSON.stringify({question}) }),
  uploadDocument: async (id: string, file: {uri:string;name:string;mimeType:string}) => { const form = new FormData(); form.append("file", { uri: file.uri, name: file.name, type: file.mimeType } as unknown as Blob); return request<unknown>(`/households/${id}/documents`, { method: "POST", body: form }); },
};

export { ApiError };
