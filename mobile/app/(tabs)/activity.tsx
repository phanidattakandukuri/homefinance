import { useMemo, useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useHousehold } from "@/lib/household";

export default function Activity() {
  const householdId = useHousehold((state) => state.householdId);
  const user = useAuth((state) => state.user);
  const [search, setSearch] = useState("");
  const [scope, setScope] = useState<"household" | "personal">("household");
  const members = useQuery({ queryKey: ["members", householdId], queryFn: () => api.members(householdId!), enabled: Boolean(householdId) });
  const transactions = useQuery({ queryKey: ["transactions", householdId, search], queryFn: () => api.transactions(householdId!, search), enabled: Boolean(householdId) });
  const currentMember = members.data?.find((member) => member.user_id === user?.id);
  const visible = useMemo(() => scope === "personal" ? transactions.data?.filter((item) => item.member_id === currentMember?.id) ?? [] : transactions.data ?? [], [scope, transactions.data, currentMember?.id]);
  const memberName = (memberId: string) => members.data?.find((member) => member.id === memberId)?.display_name ?? "Unknown member";
  if (!householdId) return <Screen><Text style={styles.title}>Activity</Text><Text style={styles.muted}>Create or join a household to view transactions.</Text></Screen>;
  return <Screen><Text style={styles.title}>Activity</Text><View style={styles.chipRow}><Pressable onPress={() => setScope("household")} style={[styles.chip, scope === "household" && styles.selectedChip]}><Text style={styles.chipText}>Household</Text></Pressable><Pressable onPress={() => setScope("personal")} style={[styles.chip, scope === "personal" && styles.selectedChip]}><Text style={styles.chipText}>Personal</Text></Pressable></View><TextInput accessibilityLabel="Search transactions" placeholder="Search merchant or description" style={styles.input} value={search} onChangeText={setSearch} /><State loading={transactions.isLoading || members.isLoading} error={(transactions.error || members.error) as Error | null} empty={visible.length === 0 ? `No ${scope} transactions have been recorded.` : undefined} />{visible.map((item) => <Text key={item.id} style={styles.card}>{memberName(item.member_id)}{"\n"}{item.merchant ?? item.description ?? item.transaction_type}{"\n"}{item.transaction_date} · {item.currency} {item.amount}</Text>)}</Screen>;
}
