import { useState } from "react";
import { Pressable, Text, TextInput } from "react-native";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api, Member } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Members() {
  const id = useHousehold((s) => s.householdId);
  const householdHydrated = useHousehold((s) => s.hydrated);
  const [joinCode, setJoinCode] = useState("");
  const [selected, setSelected] = useState<Member>();
  const [editName, setEditName] = useState("");
  const [occupation, setOccupation] = useState("");
  const [role, setRole] = useState<Member["role"]>("member");
  const q = useQuery({ queryKey: ["members", id], queryFn: () => api.members(id!), enabled: householdHydrated && !!id });
  const generate = useMutation({
    mutationFn: () => { if (!id) throw new Error("No household is selected. Create or join a household first."); return api.createJoinCode(id); },
    onSuccess: (result) => setJoinCode(result.code),
  });
  const update = useMutation({
    mutationFn: () => api.updateMember(id!, selected!.id, { display_name: editName.trim(), occupation: occupation.trim() || null, role }),
    onSuccess: () => { setSelected(undefined); void q.refetch(); },
  });
  function selectMember(member: Member) { setSelected(member); setEditName(member.display_name); setOccupation(member.occupation ?? ""); setRole(member.role); }
  return <Screen>
    <Text style={styles.title}>Household members</Text>
    <State loading={q.isLoading} error={(q.error || generate.error || update.error) as Error | null} />
    {q.data?.map((member) => <Pressable key={member.id} onPress={() => selectMember(member)}><Text style={styles.card}>{member.display_name} — {member.role} · {member.membership_status}{member.user_id ? " · linked" : " · pending"}</Text></Pressable>)}
    {selected ? <>
      <FieldLabel>Edit member profile</FieldLabel>
      <TextInput style={styles.input} placeholder="Full name" value={editName} onChangeText={setEditName} />
      <TextInput style={styles.input} placeholder="Occupation" value={occupation} onChangeText={setOccupation} />
      <Text style={styles.label}>Household access</Text>
      {(["member", "admin"] as const).map((value) => <ActionButton key={value} title={value === "admin" ? "Administrator — full household view" : "Member — personal view"} secondary={role !== value} onPress={() => setRole(value)} />)}
      <ActionButton title={update.isPending ? "Saving..." : "Save member"} disabled={!editName.trim() || update.isPending} onPress={() => void update.mutateAsync()} />
      <ActionButton title="Cancel" secondary onPress={() => setSelected(undefined)} />
    </> : null}
    <FieldLabel>Link another logged-in family member</FieldLabel>
    <Text style={styles.muted}>Generate a temporary code and share it privately. They enter it during onboarding; no email or member ID is needed.</Text>
    {!householdHydrated ? <Text style={styles.muted}>Loading household…</Text> : null}
    {!id && householdHydrated ? <Text style={styles.error}>No household is selected. Return to onboarding to create or join one.</Text> : null}
    <ActionButton title={generate.isPending ? "Generating code..." : "Generate household code"} disabled={!id || generate.isPending} onPress={() => void generate.mutateAsync()} />
    {joinCode ? <Text style={styles.card}>Share this code: {joinCode}</Text> : null}
    <ActionButton title="Refresh" secondary onPress={() => void q.refetch()} />
  </Screen>;
}
