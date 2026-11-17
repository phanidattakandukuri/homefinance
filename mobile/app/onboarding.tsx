import { router } from "expo-router";
import { useState } from "react";
import { Text, TextInput } from "react-native";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";
import { useAuth } from "@/lib/auth";

export default function Onboarding() {
  const [name, setName] = useState(""); const [joinCode, setJoinCode] = useState(""); const [generatedCode, setGeneratedCode] = useState(""); const [error, setError] = useState<Error>();
  const authenticated = useAuth((state) => state.hydrated && !!state.user);
  const setHouseholdId = useHousehold((state) => state.setHouseholdId);
  async function join() { if (!authenticated) { setError(new Error("Please log in before joining a household.")); return; } try { const member = await api.joinHousehold(joinCode); await setHouseholdId(member.household_id); router.replace("/(tabs)"); } catch (value) { setError(value instanceof Error ? value : new Error("Unable to join household.")); } }
  async function generate() { if (!authenticated) { setError(new Error("Please log in before creating a household.")); return; } try { const household = await api.createHousehold({ name: name.trim(), base_currency: "INR", timezone: "Asia/Kolkata", earning_member_names: [] }); await setHouseholdId(household.id); const result = await api.createJoinCode(household.id); setGeneratedCode(result.code); } catch (value) { setError(value instanceof Error ? value : new Error("Unable to create household code.")); } }
  return <Screen>
    <Text style={styles.title}>Set up your household</Text>
    <Text style={styles.subtitle}>Create a household, then share its join code. Other logged-in family members can enter that code to link themselves automatically.</Text>
    <FieldLabel>Household name</FieldLabel><TextInput style={styles.input} value={name} onChangeText={setName} placeholder="Our home" />
    {!authenticated ? <Text style={styles.error}>Log in first, then create or join a household.</Text> : null}<ActionButton title="Create household and join code" disabled={!authenticated || !name.trim()} onPress={() => void generate()} />{generatedCode ? <Text style={styles.card}>Share this code: {generatedCode}</Text> : null}<FieldLabel>Have a household code?</FieldLabel><TextInput style={styles.input} value={joinCode} onChangeText={setJoinCode} autoCapitalize="characters" placeholder="Enter join code" /><ActionButton title="Join household" disabled={!authenticated || joinCode.trim().length < 6} onPress={() => void join()} secondary />
    <State error={error} />
  </Screen>;
}
