import { Text } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Wealth() {
  const id = useHousehold((state) => state.householdId);
  const instruments = useQuery({ queryKey: ["instruments", id], queryFn: () => api.instruments(id!), enabled: Boolean(id) });
  const investments = useQuery({ queryKey: ["investments", id], queryFn: () => api.investments(id!), enabled: Boolean(id) });
  const assets = useQuery({ queryKey: ["assets", id], queryFn: () => api.assets(id!), enabled: Boolean(id) });
  const liabilities = useQuery({ queryKey: ["liabilities", id], queryFn: () => api.liabilities(id!), enabled: Boolean(id) });

  if (!id) return <Screen><Text style={styles.title}>Wealth</Text><Text style={styles.muted}>Create a household to load verified wealth records.</Text></Screen>;
  const error = instruments.error ?? investments.error ?? assets.error ?? liabilities.error;
  const totalAssets = assets.data?.reduce((sum, item) => sum + Number(item.current_value ?? 0), 0) ?? 0;
  const totalLiabilities = liabilities.data?.reduce((sum, item) => sum + Number(item.current_outstanding ?? 0), 0) ?? 0;
  const money = (value: number) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value);
  return <Screen>
    <Text style={styles.title}>Wealth</Text>
    <State loading={instruments.isLoading || investments.isLoading || assets.isLoading || liabilities.isLoading} error={error as Error | null} />
    <Text style={styles.card}><Text style={styles.label}>Investments{"\n"}</Text><Text style={styles.value}>{investments.data?.length ?? 0}</Text><Text style={styles.muted}> holdings across {instruments.data?.length ?? 0} instruments</Text></Text>
    <Text style={styles.card}><Text style={styles.label}>Assets{"\n"}</Text><Text style={styles.value}>{assets.data?.length ?? 0}</Text><Text style={styles.muted}> registered household assets</Text></Text>
    <Text style={styles.card}><Text style={styles.label}>Liabilities{"\n"}</Text><Text style={styles.value}>{liabilities.data?.length ?? 0}</Text><Text style={styles.muted}> outstanding liability records</Text></Text>
    <Text style={styles.card}><Text style={styles.label}>Estimated wealth snapshot{"\n"}</Text><Text style={styles.value}>{money(totalAssets - totalLiabilities)}</Text><Text style={styles.muted}>{money(totalAssets)} assets less {money(totalLiabilities)} liabilities</Text></Text>
  </Screen>;
}
