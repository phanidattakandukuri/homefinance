import { useState } from "react";
import { Button, Text, TextInput } from "react-native";
import { router } from "expo-router";
import { Screen, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
export default function ProfileEdit() { const user = useAuth((s) => s.user); const setUser = useAuth((s) => s.setUser); const [name, setName] = useState(user?.full_name ?? ""); const [message, setMessage] = useState(""); async function save() { try { const updated = await api.updateProfile({ full_name: name }); setUser(updated); setMessage("Profile updated."); setTimeout(() => router.back(), 500); } catch (e) { setMessage((e as Error).message); } } return <Screen><Text style={styles.eyebrow}>PROFILE</Text><Text style={styles.title}>Edit profile</Text><Text style={styles.subtitle}>Keep your identity details up to date across your household.</Text><Text style={styles.label}>Full name</Text><TextInput style={styles.input} value={name} onChangeText={setName} placeholder="Your name" autoCapitalize="words"/><Text style={styles.label}>Email</Text><TextInput style={[styles.input, { opacity: 0.6 }]} value={user?.email ?? ""} editable={false}/><Button title="Save changes" onPress={() => void save()} disabled={name.trim().length < 2}/>{message ? <Text style={styles.card}>{message}</Text> : null}</Screen>; }
