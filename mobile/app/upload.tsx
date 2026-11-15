import { Button, Text } from "react-native";
import * as DocumentPicker from "expo-document-picker";
import { Screen, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";
import { useState } from "react";
import { router } from "expo-router";

export default function Upload() {
  const id = useHousehold((s) => s.householdId);
  const [msg, setMsg] = useState("");

  async function pick() {
    const r = await DocumentPicker.getDocumentAsync({
      type: ["image/*", "application/pdf"],
    });

    if (r.canceled || !id) return;

    const f = r.assets[0];

    await api.uploadDocument(id, {
      uri: f.uri,
      name: f.name,
      mimeType: f.mimeType ?? "application/octet-stream",
    });

    setMsg("Uploaded. OCR requires review before transaction confirmation.");
  }

  return (
    <Screen>
      <Text style={styles.title}>Upload document</Text>

      <Text style={styles.label}>
        Documents are private and extracted values require confirmation.
      </Text>

      <Button title="Choose receipt or PDF" onPress={pick} />

      <Button title="Use camera" onPress={() => router.push("/camera-scan")} />

      <Button
        title="Review extraction"
        onPress={() => router.push("/document-review")}
      />

      {msg ? <Text style={styles.card}>{msg}</Text> : null}
    </Screen>
  );
}
