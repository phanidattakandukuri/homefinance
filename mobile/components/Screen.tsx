import { PropsWithChildren } from "react";
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

export function Screen({ children, scroll = true }: PropsWithChildren<{ scroll?: boolean }>) {
  const content = <View style={styles.content}>{children}</View>;
  return scroll ? <ScrollView contentContainerStyle={styles.screen}>{content}</ScrollView> : <View style={styles.screen}>{content}</View>;
}

export function State({ loading, error, empty }: { loading?: boolean; error?: Error | null; empty?: string }) {
  if (loading) return <ActivityIndicator accessibilityLabel="Loading" color={colors.primary} style={styles.state} />;
  if (error) return <Text accessibilityRole="alert" style={styles.error}>{error.message}</Text>;
  if (empty) return <Text style={styles.muted}>{empty}</Text>;
  return null;
}

export function FieldLabel({ children }: PropsWithChildren) {
  return <Text style={styles.label}>{children}</Text>;
}

export function ActionButton({ title, onPress, disabled = false, secondary = false }: { title: string; onPress: () => void; disabled?: boolean; secondary?: boolean }) {
  return <Pressable accessibilityRole="button" accessibilityState={{ disabled }} disabled={disabled} onPress={onPress} style={[styles.button, secondary && styles.secondaryButton, disabled && styles.disabledButton]}>
    <Text style={[styles.buttonText, secondary && styles.secondaryButtonText]}>{title}</Text>
  </Pressable>;
}

export const colors = { background: "#F5F7FB", surface: "#FFFFFF", primary: "#176B87", accent: "#F4A261", ink: "#14213D", muted: "#687386", border: "#DCE3EA", error: "#B42318" };
export const styles = StyleSheet.create({
  screen: { flexGrow: 1, backgroundColor: colors.background },
  content: { width: "100%", maxWidth: 720, alignSelf: "center", padding: 20, gap: 12 },
  title: { fontSize: 30, fontWeight: "700", color: colors.ink, marginBottom: 8 },
  subtitle: { fontSize: 16, color: colors.muted, lineHeight: 24 },
  card: { backgroundColor: colors.surface, borderRadius: 16, padding: 18, borderWidth: 1, borderColor: colors.border },
  label: { color: colors.muted, fontSize: 13, fontWeight: "600", marginBottom: 6 },
  value: { fontSize: 25, fontWeight: "700", color: colors.ink },
  input: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border, borderRadius: 10, padding: 14, color: colors.ink, fontSize: 16, marginBottom: 4 },
  button: { minHeight: 48, borderRadius: 12, justifyContent: "center", alignItems: "center", backgroundColor: colors.primary, paddingHorizontal: 18, marginTop: 4 },
  buttonText: { color: colors.surface, fontSize: 16, fontWeight: "700" },
  secondaryButton: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.primary },
  secondaryButtonText: { color: colors.primary },
  disabledButton: { opacity: 0.5 },
  error: { color: colors.error, lineHeight: 21, marginVertical: 6 },
  muted: { color: colors.muted, lineHeight: 22 },
  state: { marginVertical: 16 },
  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", gap: 12 },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: { borderWidth: 1, borderColor: colors.border, borderRadius: 20, paddingHorizontal: 12, paddingVertical: 9, backgroundColor: colors.surface },
  selectedChip: { backgroundColor: "#E6F3F7", borderColor: colors.primary },
  chipText: { color: colors.ink, fontWeight: "600" },
  modalBackdrop: { flex: 1, justifyContent: "flex-end", backgroundColor: "rgba(20,33,61,0.35)" },
  modalCard: { backgroundColor: colors.surface, borderTopLeftRadius: 22, borderTopRightRadius: 22, padding: 20, gap: 10, maxHeight: "80%" },
  modalOption: { borderBottomWidth: 1, borderBottomColor: colors.border, paddingVertical: 15 },
  badge: { backgroundColor: "#E6F3F7", paddingHorizontal: 10, paddingVertical: 5, borderRadius: 20 },
  badgeText: { color: colors.primary, fontWeight: "600" },
  eyebrow: { color: colors.primary, fontSize: 11, fontWeight: "800", letterSpacing: 1.2 },
  pageHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  heroCard: { backgroundColor: colors.primary, borderRadius: 22, padding: 22 },
  heroValue: { color: colors.surface, fontSize: 32, fontWeight: "800", marginVertical: 5 },
  metricRow: { flexDirection: "row", gap: 8, marginTop: 16 },
  metric: { flex: 1 }, metricValue: { color: colors.surface, fontSize: 14, fontWeight: "700" },
  grid: { flexDirection: "row", gap: 10 },
  statCard: { flex: 1, backgroundColor: colors.surface, borderRadius: 16, padding: 14, borderWidth: 1, borderColor: colors.border },
  statValue: { color: colors.ink, fontSize: 24, fontWeight: "800", marginTop: 10 }, statLabel: { color: colors.ink, fontWeight: "700", marginTop: 2 }, statHint: { color: colors.muted, fontSize: 12, marginTop: 3 },
  sectionTitle: { color: colors.ink, fontSize: 18, fontWeight: "800", marginTop: 8 }, infoCard: { backgroundColor: "#E6F3F7", borderRadius: 16, padding: 16 },
  segment: { flexDirection: "row", backgroundColor: colors.surface, borderRadius: 12, padding: 4, borderWidth: 1, borderColor: colors.border }, segmentItem: { flex: 1, alignItems: "center", paddingVertical: 10, borderRadius: 9 }, segmentActive: { backgroundColor: "#E6F3F7" }, segmentText: { color: colors.ink, fontWeight: "700" },
  smallMetric: { flex: 1, backgroundColor: colors.surface, borderRadius: 14, padding: 14, borderWidth: 1, borderColor: colors.border }, smallValue: { color: colors.ink, fontWeight: "800", fontSize: 16 },
  barBlock: { marginTop: 12 }, barLabel: { flexDirection: "row", justifyContent: "space-between" }, barTrack: { height: 8, backgroundColor: "#EAF0F3", borderRadius: 10, overflow: "hidden" }, barFill: { height: 8, backgroundColor: colors.accent, borderRadius: 10 },
  profileHeader: { flexDirection: "row", alignItems: "center", gap: 16, paddingVertical: 8 }, avatar: { width: 76, height: 76, borderRadius: 38, backgroundColor: colors.primary, justifyContent: "center", alignItems: "center" }, avatarText: { color: colors.surface, fontSize: 32, fontWeight: "800" }, profileIdentity: { flex: 1 }, profileName: { color: colors.ink, fontSize: 21, fontWeight: "800" }, profileHandle: { color: colors.primary, fontSize: 12, marginTop: 4, fontWeight: "600" }, profileStats: { flexDirection: "row", backgroundColor: colors.surface, borderRadius: 16, padding: 16, borderWidth: 1, borderColor: colors.border }, profileStat: { flex: 1, alignItems: "center" }, profileStatValue: { color: colors.ink, fontWeight: "800", fontSize: 16 }, menuRow: { flexDirection: "row", alignItems: "center", gap: 14, backgroundColor: colors.surface, borderRadius: 15, padding: 15, borderWidth: 1, borderColor: colors.border }, menuCopy: { flex: 1 }, menuTitle: { color: colors.ink, fontWeight: "700", fontSize: 15 }, menuSubtitle: { color: colors.muted, fontSize: 12, marginTop: 3 },
  preferenceHero: { backgroundColor: colors.primary, borderRadius: 20, padding: 20 },
  historyCard: { backgroundColor: colors.surface, borderRadius: 16, padding: 17, borderWidth: 1, borderColor: colors.border, flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  historyPeriod: { color: colors.ink, fontWeight: "800", fontSize: 15 }, historyValue: { color: colors.primary, fontWeight: "800", fontSize: 17 },
});
