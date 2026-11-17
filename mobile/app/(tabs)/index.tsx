import { router } from "expo-router";
import { Pressable, Text, View } from "react-native";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ActionButton, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";
import { useAuth } from "@/lib/auth";

const money = (value: number | string | null | undefined, currency = "INR") => value == null ? "—" : new Intl.NumberFormat("en-IN", { style: "currency", currency, maximumFractionDigits: 0 }).format(Number(value));

export default function Home() {
  const householdId = useHousehold((state) => state.householdId);
  const user = useAuth((state) => state.user);
  const members = useQuery({ queryKey: ["members", householdId], queryFn: () => api.members(householdId!), enabled: Boolean(householdId) });
  const [scope, setScope] = useState<"household" | "personal">("household");
  const personalMember = members.data?.find((member) => member.user_id === user?.id);
  const query = useQuery({ queryKey: ["dashboard", householdId, scope, personalMember?.id], queryFn: () => scope === "personal" && personalMember ? api.memberDashboard(householdId!, personalMember.id) : api.dashboard(householdId!), enabled: Boolean(householdId && (scope === "household" || personalMember)) });
  if (!householdId) return <Screen><Text style={styles.title}>Your household</Text><Text style={styles.subtitle}>Create a household before the dashboard can load verified financial data.</Text><ActionButton title="Start onboarding" onPress={() => router.push("/onboarding")} /></Screen>;
  return <Screen><Text style={styles.title}>{scope === "household" ? "Household overview" : "My financial overview"}</Text><View style={styles.chipRow}><Pressable style={[styles.chip, scope === "household" && styles.selectedChip]} onPress={() => setScope("household")}><Text style={styles.chipText}>Household</Text></Pressable><Pressable style={[styles.chip, scope === "personal" && styles.selectedChip]} onPress={() => setScope("personal")}><Text style={styles.chipText}>My overview</Text></Pressable></View><State loading={query.isLoading || members.isLoading} error={(query.error || members.error) as Error | null} />
    {query.data && <View style={styles.card}><Text style={styles.label}>Net worth</Text><Text style={styles.value}>{money(query.data.net_worth)}</Text><View style={styles.row}><Metric label="Income" value={money(query.data.total_income)} /><Metric label="Expenses" value={money(query.data.total_expenses)} /></View><View style={styles.row}><Metric label="Savings" value={money(query.data.monthly_savings)} /><Metric label="Investments" value={money(query.data.total_investments)} /></View></View>}
    {query.data && <Text style={styles.muted}>Period: {query.data.period_start} to {query.data.period_end}</Text>}
  </Screen>;
}

function Metric({ label, value }: { label: string; value: string }) { return <View style={{ flex: 1, marginTop: 18 }}><Text style={styles.label}>{label}</Text><Text style={{ color: styles.value.color, fontWeight: "700" }}>{value}</Text></View>; }
