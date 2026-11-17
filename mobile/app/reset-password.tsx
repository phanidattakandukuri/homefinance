import { useState } from "react";
import { Text, TextInput } from "react-native";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";

export default function ResetPassword() {
  const [email, setEmail] = useState(""); const [token, setToken] = useState(""); const [next, setNext] = useState(""); const [message, setMessage] = useState(""); const [error, setError] = useState<Error>(); const [requested, setRequested] = useState(false);
  async function request() { setError(undefined); try { const result = await api.requestPasswordReset(email.trim()); setMessage(result.message); if (result.reset_token) setToken(result.reset_token); setRequested(true); } catch (value) { setError(value instanceof Error ? value : new Error("Unable to prepare reset.")); } }
  async function confirm() { setError(undefined); try { await api.resetPassword({ reset_token: token, new_password: next }); setMessage("Password reset successfully. You can log in now."); } catch (value) { setError(value instanceof Error ? value : new Error("Unable to reset password.")); } }
  return <Screen><Text style={styles.title}>Reset password</Text><State error={error} />{!requested ? <><FieldLabel>Account email</FieldLabel><TextInput style={styles.input} autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} /><ActionButton title="Prepare reset" disabled={!email.trim()} onPress={() => void request()} /></> : <><Text style={styles.card}>{message}</Text><FieldLabel>Reset token</FieldLabel><TextInput style={styles.input} value={token} onChangeText={setToken} /><FieldLabel>New password</FieldLabel><TextInput style={styles.input} secureTextEntry value={next} onChangeText={setNext} /><ActionButton title="Set new password" disabled={token.length < 20 || next.length < 8} onPress={() => void confirm()} /></>}</Screen>;
}
