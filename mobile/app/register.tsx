import { router } from "expo-router";
import { useState } from "react";
import { Text, TextInput } from "react-native";

import {
  ActionButton,
  FieldLabel,
  Screen,
  State,
  styles,
} from "@/components/Screen";

import { api } from "@/lib/api";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (!name.trim() || !email.trim() || password.length < 8) {
      setError(new Error("Please enter valid registration details."));
      return;
    }

    try {
      setLoading(true);
      setError(undefined);

      await api.register({
        full_name: name.trim(),
        email: email.trim().toLowerCase(),
        password,
      });

      // Registration successful: navigate to login.
      router.replace("/login");
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err
          : new Error("Registration failed. Please try again."),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen>
      <Text style={styles.title}>Create your account</Text>

      <FieldLabel>Full name</FieldLabel>
      <TextInput
        style={styles.input}
        value={name}
        onChangeText={setName}
        placeholder="Enter your full name"
        autoCapitalize="words"
      />

      <FieldLabel>Email</FieldLabel>
      <TextInput
        autoCapitalize="none"
        keyboardType="email-address"
        style={styles.input}
        value={email}
        onChangeText={setEmail}
        placeholder="Enter your email"
      />

      <FieldLabel>Password (at least 8 characters)</FieldLabel>
      <TextInput
        secureTextEntry
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        placeholder="Create a password"
      />

      <State error={error} />

      <ActionButton
        title={loading ? "Creating account..." : "Register"}
        disabled={
          loading || !name.trim() || !email.trim() || password.length < 8
        }
        onPress={() => void submit()}
      />
    </Screen>
  );
}
