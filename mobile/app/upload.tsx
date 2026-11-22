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

    const document = await api.uploadDocument(id, {
      uri: f.uri,
      name: f.name,
      mimeType: f.mimeType ?? "application/octet-stream",
    });

    setMsg("Uploaded. Processing OCR…");
    for (let attempt = 0; attempt < 20; attempt += 1) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const job = await api.ocrJob(id, document.id);
      if (job.status === "completed") { setMsg("OCR completed. Opening review…"); router.push(`/document-review?documentId=${document.id}`); return; }
      if (job.status === "failed") { setMsg(`OCR failed: ${job.last_error ?? "check the document and try again"}`); return; }
    }
    setMsg(`OCR is still processing. Document ID: ${document.id}`);
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
        onPress={() => setMsg("Choose a document first; review opens automatically after OCR completes.")}
      />

      {msg ? <Text style={styles.card}>{msg}</Text> : null}
    </Screen>
  );
}
