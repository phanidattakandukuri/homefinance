import { router } from "expo-router";
import { Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { ActionButton, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";

const money = (value: number | string | null | undefined, currency = "INR") => value == null ? "—" : new Intl.NumberFormat("en-IN", { style: "currency", currency, maximumFractionDigits: 0 }).format(Number(value));

export default function Home() {
  const householdId = useHousehold((state) => state.householdId);
  const query = useQuery({ queryKey: ["dashboard", householdId], queryFn: () => api.dashboard(householdId!), enabled: Boolean(householdId) });
  if (!householdId) return <Screen><Text style={styles.title}>Your household</Text><Text style={styles.subtitle}>Create a household before the dashboard can load verified financial data.</Text><ActionButton title="Start onboarding" onPress={() => router.push("/onboarding")} /></Screen>;
  return <Screen><Text style={styles.title}>Household overview</Text><State loading={query.isLoading} error={query.error as Error | null} />
    {query.data && <View style={styles.card}><Text style={styles.label}>Net worth</Text><Text style={styles.value}>{money(query.data.net_worth)}</Text><View style={styles.row}><Metric label="Income" value={money(query.data.total_income)} /><Metric label="Expenses" value={money(query.data.total_expenses)} /></View><View style={styles.row}><Metric label="Savings" value={money(query.data.monthly_savings)} /><Metric label="Investments" value={money(query.data.total_investments)} /></View></View>}
    {query.data && <Text style={styles.muted}>Period: {query.data.period_start} to {query.data.period_end}</Text>}
  </Screen>;
}

function Metric({ label, value }: { label: string; value: string }) { return <View style={{ flex: 1, marginTop: 18 }}><Text style={styles.label}>{label}</Text><Text style={{ color: styles.value.color, fontWeight: "700" }}>{value}</Text></View>; }
