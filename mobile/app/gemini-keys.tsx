import { useEffect, useState } from "react";
import { Button, Text, TextInput } from "react-native";
import { Screen, styles } from "@/components/Screen";
import { api, GeminiKey } from "@/lib/api";

export default function GeminiKeys() {
  const [keys, setKeys] = useState<GeminiKey[]>([]); const [value, setValue] = useState(""); const [message, setMessage] = useState("");
  async function load() { try { setKeys(await api.geminiKeys()); } catch (error) { setMessage((error as Error).message); } }
  useEffect(() => { void load(); }, []);
  async function add() { try { await api.addGeminiKey({ api_key: value }); setValue(""); setMessage("Key added and activated."); await load(); } catch (error) { setMessage((error as Error).message); } }
  async function activate(id: string) { await api.activateGeminiKey(id); await load(); setMessage("Active key switched."); }
  return <Screen><Text style={styles.title}>HomeFin AI keys</Text><Text style={styles.subtitle}>Create a Gemini API key at aistudio.google.com/apikey, copy it, and paste it here. Your key is used only for your account. Add another key when a limit is reached, then switch between keys.</Text><TextInput style={styles.input} placeholder="Paste Gemini API key (AIza...)" value={value} onChangeText={setValue} secureTextEntry /><Button title="Add and use this key" onPress={() => void add()} disabled={!value.trim()} />{keys.map((item) => <Text style={styles.card} key={item.id}>{item.label} ••••{item.last_four}{item.is_active ? " (active)" : ""}{!item.is_active ? <Button title="Use this key" onPress={() => void activate(item.id)} /> : null}</Text>)}{message ? <Text style={styles.card}>{message}</Text> : null}</Screen>;
}
