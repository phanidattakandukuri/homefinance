import { router } from "expo-router";
import { Text } from "react-native";
import { ActionButton, Screen, styles } from "@/components/Screen";

export default function Welcome() {
  return <Screen>
    <Text style={styles.title}>HomeFin AI</Text>
    <Text style={styles.subtitle}>A private, shared view of your household finances. Your backend remains the source of truth for every figure.</Text>
    <Text style={[styles.card, styles.subtitle]}>Start with an account, then create your household and add members.</Text>
    <ActionButton title="Log in" onPress={() => router.push("/login")} />
    <ActionButton title="Create account" secondary onPress={() => router.push("/register")} />
  </Screen>;
}
