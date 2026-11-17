import { router } from "expo-router";
import { useState } from "react";
import { Text, TextInput } from "react-native";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { useAuth } from "@/lib/auth";

export default function Login() {
  const login = useAuth((state) => state.login);
  const loading = useAuth((state) => state.loading);
  const error = useAuth((state) => state.error);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  async function submit() { await login(email.trim(), password); router.replace("/(tabs)"); }
  return <Screen>
    <Text style={styles.title}>Log in</Text>
    <FieldLabel>Email</FieldLabel><TextInput accessibilityLabel="Email" autoCapitalize="none" keyboardType="email-address" style={styles.input} value={email} onChangeText={setEmail} />
    <FieldLabel>Password</FieldLabel><TextInput accessibilityLabel="Password" secureTextEntry style={styles.input} value={password} onChangeText={setPassword} />
    <State error={error ? new Error(error) : undefined} loading={loading} />
    <ActionButton title="Log in" disabled={loading || !email || !password} onPress={() => void submit()} />
    <ActionButton title="Forgot password" secondary onPress={() => router.push("/reset-password")} />
    <ActionButton title="Create account" secondary onPress={() => router.push("/register")} />
  </Screen>;
}
