/**
 * HomeFin API smoke/seed script.
 *
 * Usage:
 *   node bruno.mjs
 *   API_BASE_URL=http://127.0.0.1:8000 node bruno.mjs
 *
 * The script creates an isolated sample user and household, then exercises
 * every currently registered v1 API operation. IDs are captured from the
 * responses, so no real database identifiers or credentials are required.
 */

const base = (process.env.API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const api = `${base}/api/v1`;
const runId = Date.now();
const email = `bruno-${runId}@example.test`;
const password = "BrunoSamplePassword123!";

let accessToken;
let refreshToken;
let householdId;
let ownerMemberId;
let sampleMemberId;
let categoryId;
let transactionId;
let salaryId;
let budgetId;
let investmentId;
let instrumentId;
let documentId;

async function request(method, path, body, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  let payload = body;
  if (body !== undefined && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  const response = await fetch(`${api}${path}`, { method, headers, body: payload });
  const text = await response.text();
  let data;
  try { data = text ? JSON.parse(text) : undefined; } catch { data = text; }
  if (!response.ok) {
    console.warn(`!! ${method} ${path} -> ${response.status}`, data);
    return data;
  }
  console.log(`OK ${method} ${path} -> ${response.status}`);
  return data;
}

const uuid = () => "00000000-0000-0000-0000-000000000001";

async function main() {
  // Health
  await request("GET", "/health");
  await request("GET", "/health/database");

  // Authentication
  await request("POST", "/auth/register", { email, password, full_name: "Bruno Sample User" });
  const login = await request("POST", "/auth/login", { email, password });
  accessToken = login.access_token;
  refreshToken = login.refresh_token;
  await request("GET", "/auth/me");
  const refreshed = await request("POST", `/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`);
  accessToken = refreshed.access_token;
  refreshToken = refreshed.refresh_token;

  // Household and members
  const household = await request("POST", "/households", {
    name: "Bruno Sample Household", base_currency: "INR", timezone: "Asia/Calcutta",
    earning_member_names: ["Sample Partner"],
  });
  householdId = household.id;
  ownerMemberId = household.members.find((m) => m.role === "owner")?.id;
  sampleMemberId = household.members.find((m) => m.display_name === "Sample Partner")?.id;
  await request("GET", `/households/${householdId}`);
  await request("PATCH", `/households/${householdId}`, { name: "Bruno Sample Household Updated" });
  const members = await request("GET", `/households/${householdId}/members`);
  if (!sampleMemberId) sampleMemberId = members.find((m) => m.role !== "owner")?.id;
  const extraMember = await request("POST", `/households/${householdId}/members`, {
    display_name: "Temporary Sample Member", role: "member",
  });
  await request("PATCH", `/households/${householdId}/members/${extraMember.id}`, { role: "viewer" });
  await request("DELETE", `/households/${householdId}/members/${extraMember.id}`);

  // Categories and transactions
  const category = await request("POST", `/households/${householdId}/categories`, { name: "Bruno Groceries" });
  categoryId = category.id;
  await request("GET", `/households/${householdId}/categories`);
  const transaction = await request("POST", `/households/${householdId}/transactions`, {
    member_id: ownerMemberId, category_id: categoryId, transaction_type: "expense",
    amount: 2450.75, currency: "INR", transaction_date: "2026-01-15",
    description: "Sample grocery purchase", merchant: "Sample Market",
    payment_method: "card", notes: "Created by bruno.mjs", source: "bruno",
    reference_number: `BRUNO-${runId}`,
  }, { headers: { "X-Idempotency-Key": `bruno-${runId}` } });
  transactionId = transaction.id;
  await request("GET", `/households/${householdId}/transactions?transaction_type=expense&page=1&page_size=50&search=Sample`);
  await request("GET", `/households/${householdId}/transactions/${transactionId}/duplicates`);
  await request("PATCH", `/households/${householdId}/transactions/${transactionId}`, { notes: "Updated sample note" });

  // Salary
  const salary = await request("POST", `/households/${householdId}/members/${ownerMemberId}/salary`, {
    employer_name: "Sample Technologies", designation: "Software Engineer", salary_type: "annual_ctc",
    annual_ctc: 1800000, monthly_gross: 150000, monthly_in_hand: 112500,
    basic_salary: 75000, hra: 30000, special_allowance: 45000, employee_pf: 9000,
    employer_pf: 9000, tds: 18500, effective_from: "2026-01-01",
  });
  salaryId = salary.id;
  await request("GET", `/households/${householdId}/members/${ownerMemberId}/salary`);
  await request("GET", `/households/${householdId}/members/${ownerMemberId}/salary/current`);
  await request("GET", `/households/${householdId}/members/${ownerMemberId}/salary/${salaryId}/breakdown`);
  await request("PATCH", `/households/${householdId}/members/${ownerMemberId}/salary/${salaryId}`, { designation: "Senior Software Engineer" });
  await request("POST", `/households/${householdId}/members/${sampleMemberId}/salary/revision`, {
    employer_name: "Sample Consulting", designation: "Analyst", monthly_in_hand: 65000,
    effective_from: "2026-02-01",
  });

  // Wealth
  const instrument = await request("POST", `/households/${householdId}/wealth/instruments`, {
    name: "Sample Index Fund", category: "mutual_fund", identifier: "SAMPLE-INDEX-001", currency: "INR",
  });
  instrumentId = instrument.id;
  const investment = await request("POST", `/households/${householdId}/wealth/investments`, {
    member_id: ownerMemberId, instrument_id: instrumentId, notes: "Sample investment",
  });
  investmentId = investment.id;
  await request("GET", `/households/${householdId}/wealth/instruments`);
  await request("GET", `/households/${householdId}/wealth/investments`);
  await request("POST", `/households/${householdId}/wealth/investments/${investmentId}/transactions`, {
    transaction_type: "buy", quantity: 10, unit_price: 250, fees: 5, cash_flow: 2505,
    transaction_date: "2026-01-10", notes: "Sample purchase",
  });
  await request("POST", `/households/${householdId}/wealth/investments/${investmentId}/valuations`, {
    valuation_date: "2026-01-31", quantity: 10, unit_price: 265, current_value: 2650,
    source: "manual", notes: "Sample month-end valuation",
  });
  const asset = await request("POST", `/households/${householdId}/wealth/assets`, {
    member_id: ownerMemberId, name: "Sample Emergency Fund", category: "cash",
    acquisition_cost: 100000, current_value: 100000, acquisition_date: "2026-01-01", valuation_date: "2026-01-31",
  });
  await request("GET", `/households/${householdId}/wealth/assets`);
  await request("POST", `/households/${householdId}/wealth/liabilities`, {
    member_id: ownerMemberId, name: "Sample Home Loan", category: "mortgage",
    original_principal: 5000000, current_outstanding: 4750000, interest_rate: 8.5, emi: 45000,
    start_date: "2025-01-01", end_date: "2045-01-01",
  });
  await request("GET", `/households/${householdId}/wealth/liabilities`);

  // Planning
  const budget = await request("POST", `/households/${householdId}/budgets`, {
    member_id: ownerMemberId, category_id: categoryId, name: "Monthly groceries",
    amount: 15000, period_start: "2026-01-01", period_end: "2026-01-31",
  });
  budgetId = budget.id;
  await request("GET", `/households/${householdId}/budgets`);
  await request("GET", `/households/${householdId}/budgets/${budgetId}/progress`);
  await request("POST", `/households/${householdId}/goals`, {
    member_id: ownerMemberId, name: "Sample vacation fund", goal_type: "savings",
    target_amount: 200000, current_amount: 25000, target_date: "2026-12-31",
  });
  await request("GET", `/households/${householdId}/goals`);
  await request("POST", `/households/${householdId}/recurring`, {
    member_id: ownerMemberId, category_id: categoryId, name: "Sample monthly groceries",
    transaction_type: "expense", amount: 12000, frequency: "monthly", next_run_date: "2026-02-01",
    payload: { source: "bruno" },
  });
  await request("GET", `/households/${householdId}/recurring`);

  // Analytics and assistant
  await request("GET", `/households/${householdId}/analytics/household?period_type=calendar_year`);
  await request("GET", `/households/${householdId}/analytics/members/${ownerMemberId}?period_type=current_month`);
  await request("POST", `/households/${householdId}/analytics/snapshots?start=2026-01-01&end=2026-01-31&reason=bruno`);
  await request("GET", `/households/${householdId}/analytics/snapshots`);
  await request("POST", `/households/${householdId}/assistant/ask`, {
    question: "Summarize my household spending, investments, and net worth.",
    start: "2026-01-01", end: "2026-01-31",
  });

  // Documents: valid tiny PNG; OCR/extraction may remain unavailable when no OCR provider is configured.
  const form = new FormData();
  form.append("file", new Blob([Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=", "base64")], { type: "image/png" }), "sample.png");
  form.append("document_type", "receipt");
  const document = await request("POST", `/households/${householdId}/documents`, form);
  documentId = document.id;
  await request("GET", `/households/${householdId}/documents/${documentId}`);
  await request("GET", `/households/${householdId}/documents/${documentId}/extraction`);
  await request("POST", `/households/${householdId}/documents/${documentId}/confirm`, { merchant: "Sample Market", amount: 2450.75 });
  await request("POST", `/households/${householdId}/documents/${documentId}/reject`);

  // Void the sample transaction last so all transaction endpoints were exercised.
  await request("DELETE", `/households/${householdId}/transactions/${transactionId}`);
  await request("POST", "/auth/logout");
  console.log(`\nCompleted Bruno sample run for ${email}`);
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
