import { Text } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Wealth(){const id=useHousehold(s=>s.householdId);const inv=useQuery({queryKey:["investments",id],queryFn:()=>api.investments(id!),enabled:!!id});const assets=useQuery({queryKey:["assets",id],queryFn:()=>api.assets(id!),enabled:!!id});const liabilities=useQuery({queryKey:["liabilities",id],queryFn:()=>api.liabilities(id!),enabled:!!id});return <Screen><Text style={styles.title}>Wealth</Text><State loading={inv.isLoading} error={(inv.error||assets.error||liabilities.error) as Error}/><Text style={styles.card}>Investments: {inv.data?.length??0}</Text><Text style={styles.card}>Assets: {assets.data?.length??0}</Text><Text style={styles.card}>Liabilities: {liabilities.data?.length??0}</Text></Screen>}
