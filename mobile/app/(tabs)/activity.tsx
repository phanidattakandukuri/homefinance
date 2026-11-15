import { useState } from "react";
import { Text, TextInput } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Activity() {
  const householdId = useHousehold((state) => state.householdId);
  const [search, setSearch] = useState("");
  const query = useQuery({ queryKey: ["transactions", householdId, search], queryFn: () => api.transactions(householdId!, search), enabled: Boolean(householdId) });
  return <Screen><Text style={styles.title}>Activity</Text>{!householdId ? <Text style={styles.muted}>Create a household to view transactions.</Text> : <><TextInput accessibilityLabel="Search transactions" placeholder="Search merchant or description" style={styles.input} value={search} onChangeText={setSearch} /><State loading={query.isLoading} error={query.error as Error | null} empty={query.data?.length === 0 ? "No transactions have been recorded for this household." : undefined} />{query.data?.map((item) => <Text key={item.id} style={styles.card}>{item.merchant ?? item.description ?? item.transaction_type}{"\n"}{item.transaction_date} · {item.currency} {item.amount}</Text>)}</>}</Screen>;
}
