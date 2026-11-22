import { useEffect, useState } from "react";
import { Button, Text } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Screen, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";
export default function DocumentReview() { const id = useHousehold((s) => s.householdId); const { documentId } = useLocalSearchParams<{ documentId?: string }>(); const [message, setMessage] = useState("Loading extraction…"); const [ready, setReady] = useState(false); useEffect(() => { if (!id || !documentId) { setMessage("Upload a document first."); return; } void api.extraction(id, documentId).then((e) => { setReady(true); setMessage(`Amount: ${e.amount ?? "unknown"}\nMerchant: ${e.merchant ?? "unknown"}\n\n${e.raw_extracted_text ?? "No text was detected."}`); }).catch((e: Error) => setMessage(e.message)); }, [id, documentId]); async function confirm() { if (!id || !documentId) return; await api.confirmExtraction(id, documentId, {}); setMessage("Reviewed and confirmed. It can now be used for a transaction."); } return <Screen><Text style={styles.title}>Review document</Text><Text style={styles.card}>{message}</Text><Button title="Confirm reviewed data" onPress={() => void confirm()} disabled={!ready}/></Screen>; }
