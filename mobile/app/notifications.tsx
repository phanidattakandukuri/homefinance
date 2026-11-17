import { useEffect, useState } from "react";
import { Button, Text, TextInput } from "react-native";
import { Screen, styles } from "@/components/Screen";
import { api, NotificationPreferences } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Notifications() {
  const id = useHousehold((state) => state.householdId); const [settings, setSettings] = useState<NotificationPreferences>(); const [message, setMessage] = useState("");
  useEffect(() => { if (id) void api.notificationPreferences(id).then(setSettings).catch((error: Error) => setMessage(error.message)); }, [id]);
  async function save() { if (!id || !settings) return; const result = await api.updateNotificationPreferences(id, { enabled: settings.enabled, recurring_reminders: settings.recurring_reminders, budget_alerts: settings.budget_alerts, goal_reminders: settings.goal_reminders, channel: settings.channel }); setSettings(result); setMessage("Notification preferences saved."); }
  return <Screen><Text style={styles.title}>Notifications</Text>{settings ? <><Text style={styles.card}>Channel: {settings.channel}</Text><TextInput style={styles.input} value={settings.channel} onChangeText={(channel) => setSettings({ ...settings, channel: channel as NotificationPreferences["channel"] })} placeholder="push, email, or none"/><Button title={settings.enabled ? "Disable notifications" : "Enable notifications"} onPress={() => setSettings({ ...settings, enabled: !settings.enabled })}/><Button title={`Recurring reminders: ${settings.recurring_reminders ? "on" : "off"}`} onPress={() => setSettings({ ...settings, recurring_reminders: !settings.recurring_reminders })}/><Button title={`Budget alerts: ${settings.budget_alerts ? "on" : "off"}`} onPress={() => setSettings({ ...settings, budget_alerts: !settings.budget_alerts })}/><Button title={`Goal reminders: ${settings.goal_reminders ? "on" : "off"}`} onPress={() => setSettings({ ...settings, goal_reminders: !settings.goal_reminders })}/><Button title="Save preferences" onPress={() => void save()}/></> : <Text style={styles.card}>Loading notification preferences…</Text>}{message ? <Text style={styles.card}>{message}</Text> : null}</Screen>;
}
