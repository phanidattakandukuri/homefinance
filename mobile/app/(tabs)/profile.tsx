import { router } from "expo-router";
import { Text } from "react-native";
import { ActionButton, Screen, styles } from "@/components/Screen";
import { useAuth } from "@/lib/auth";
import { useHousehold } from "@/lib/household";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function Profile() {
  const user = useAuth((state) => state.user); const logout = useAuth((state) => state.logout); const householdId = useHousehold((state) => state.householdId);
  const household = useQuery({ queryKey: ["household", householdId], queryFn: () => api.household(householdId!), enabled: Boolean(householdId) });
  return <Screen><Text style={styles.title}>Profile</Text><Text style={styles.card}>{user?.full_name}{"\n"}{user?.email}</Text>{household.data && <Text style={styles.card}>{household.data.name}{"\n"}{household.data.members.length} household member(s)</Text>}<ActionButton title="Household members" secondary onPress={() => router.push("/members")} /><ActionButton title="Salary details" secondary onPress={() => router.push("/salary")} /><ActionButton title="Net worth history" secondary onPress={() => router.push("/snapshots")} /><ActionButton title="Household onboarding" secondary onPress={() => router.push("/onboarding")} /><ActionButton title="Log out" onPress={() => void logout().then(() => router.replace("/welcome"))} /></Screen>;
}
