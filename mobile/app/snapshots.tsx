import { Text } from "react-native";
import { Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";
import { useQuery } from "@tanstack/react-query";

export default function Snapshots() {
  const id = useHousehold((s) => s.householdId);

  const q = useQuery({
    queryKey: ["snapshots", id],
    queryFn: () => api.snapshots(id!),
    enabled: !!id,
  });

  return (
    <Screen>
      <Text style={styles.title}>Net worth history</Text>

      <State loading={q.isLoading} error={q.error as Error} />

      {q.data?.map((x: any) => (
        <Text key={x.id} style={styles.card}>
          {x.period_start} to {x.period_end}
          {"\n"}
          Net worth: {x.payload?.net_worth ?? "not available"}
        </Text>
      ))}
    </Screen>
  );
}
