import { useState } from "react";
import { Text, TextInput } from "react-native";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";

export default function Password() {
  const [current, setCurrent] = useState(""); const [next, setNext] = useState(""); const [message, setMessage] = useState(""); const [error, setError] = useState<Error>(); const [saving, setSaving] = useState(false);
  async function save() { setSaving(true); setError(undefined); setMessage(""); try { await api.changePassword({ current_password: current, new_password: next }); setCurrent(""); setNext(""); setMessage("Password changed successfully."); } catch (value) { setError(value instanceof Error ? value : new Error("Unable to change password.")); } finally { setSaving(false); } }
  return <Screen><Text style={styles.title}>Change password</Text><State error={error} /><FieldLabel>Current password</FieldLabel><TextInput style={styles.input} secureTextEntry value={current} onChangeText={setCurrent} /><FieldLabel>New password</FieldLabel><TextInput style={styles.input} secureTextEntry value={next} onChangeText={setNext} /><ActionButton title={saving ? "Saving..." : "Change password"} disabled={saving || !current || next.length < 8} onPress={() => void save()} />{message ? <Text style={styles.card}>{message}</Text> : null}</Screen>;
}
