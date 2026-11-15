import { router } from "expo-router";
import { Text } from "react-native";
import { ActionButton, Screen, styles } from "@/components/Screen";

export default function Add() {
  return <Screen><Text style={styles.title}>Add</Text><Text style={styles.subtitle}>Create a verified record in your household ledger.</Text><ActionButton title="Add income or expense" onPress={() => router.push("/transaction")} /><ActionButton title="Upload receipt" secondary onPress={() => router.push("/upload")} /><ActionButton title="Scan document" secondary onPress={() => router.push("/upload")} /><ActionButton title="Ask HomeFin AI" secondary onPress={() => router.push("/assistant")} /><Text style={styles.muted}>Transfers and investment transactions require account and instrument selection; those forms remain unavailable until account selection is added.</Text></Screen>;
}
