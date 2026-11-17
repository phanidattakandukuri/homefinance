import { router } from "expo-router";
import { Text } from "react-native";
import { ActionButton, Screen, styles } from "@/components/Screen";

export default function Add() {
  return <Screen><Text style={styles.title}>Add</Text><Text style={styles.subtitle}>Create a verified record in your household ledger.</Text><ActionButton title="Add income or expense" onPress={() => router.push("/transaction")} /><ActionButton title="Add asset" secondary onPress={() => router.push("/asset")} /><ActionButton title="Add investment" secondary onPress={() => router.push("/investment")} /><ActionButton title="Add loan or liability" secondary onPress={() => router.push("/liability")} /><ActionButton title="Upload receipt" secondary onPress={() => router.push("/upload")} /><ActionButton title="Ask HomeFin AI" secondary onPress={() => router.push("/assistant")} /><Text style={styles.muted}>Investment contributions and transfers remain separate from consumption expenses.</Text></Screen>;
}
