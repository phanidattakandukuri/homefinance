import { router } from "expo-router";
import { useState } from "react";
import { Text, TextInput } from "react-native";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Onboarding() {
  const [name, setName] = useState(""); const [members, setMembers] = useState(""); const [error, setError] = useState<Error>();
  const setHouseholdId = useHousehold((state) => state.setHouseholdId);
  async function submit() {
    try {
      const household = await api.createHousehold({ name: name.trim(), base_currency: "INR", timezone: "Asia/Kolkata", earning_member_names: members.split(",").map((item) => item.trim()).filter(Boolean) });
      await setHouseholdId(household.id);
      router.replace("/(tabs)");
    } catch (value) { setError(value instanceof Error ? value : new Error("Unable to create household.")); }
  }
  return <Screen>
    <Text style={styles.title}>Set up your household</Text>
    <Text style={styles.subtitle}>The backend will create the household and its initial earning-member profiles. You can add linked users later.</Text>
    <FieldLabel>Household name</FieldLabel><TextInput style={styles.input} value={name} onChangeText={setName} placeholder="Our home" />
    <FieldLabel>Other earning members (comma separated, optional)</FieldLabel><TextInput style={styles.input} value={members} onChangeText={setMembers} placeholder="Alex, Priya" />
    <State error={error} />
    <ActionButton title="Create household" disabled={!name.trim()} onPress={() => void submit()} />
  </Screen>;
}
