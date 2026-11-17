import { useState } from "react";
import { Pressable, Text, TextInput } from "react-native";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api, Member } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Members() {
  const id = useHousehold((s) => s.householdId);
  const [joinCode, setJoinCode] = useState("");
  const [selected, setSelected] = useState<Member>();
  const [editName, setEditName] = useState("");
  const [occupation, setOccupation] = useState("");
  const q = useQuery({ queryKey: ["members", id], queryFn: () => api.members(id!), enabled: !!id });
  const generate = useMutation({
    mutationFn: () => api.createJoinCode(id!),
    onSuccess: (result) => setJoinCode(result.code),
  });
  const update = useMutation({
    mutationFn: () => api.updateMember(id!, selected!.id, { display_name: editName.trim(), occupation: occupation.trim() || null }),
    onSuccess: () => { setSelected(undefined); void q.refetch(); },
  });
  function selectMember(member: Member) { setSelected(member); setEditName(member.display_name); setOccupation(member.occupation ?? ""); }
  return <Screen>
    <Text style={styles.title}>Household members</Text>
    <State loading={q.isLoading} error={(q.error || generate.error || update.error) as Error | null} />
    {q.data?.map((member) => <Pressable key={member.id} onPress={() => selectMember(member)}><Text style={styles.card}>{member.display_name} — {member.role} · {member.membership_status}{member.user_id ? " · linked" : " · pending"}</Text></Pressable>)}
    {selected ? <>
      <FieldLabel>Edit member profile</FieldLabel>
      <TextInput style={styles.input} placeholder="Full name" value={editName} onChangeText={setEditName} />
      <TextInput style={styles.input} placeholder="Occupation" value={occupation} onChangeText={setOccupation} />
      <ActionButton title={update.isPending ? "Saving..." : "Save member"} disabled={!editName.trim() || update.isPending} onPress={() => void update.mutateAsync()} />
      <ActionButton title="Cancel" secondary onPress={() => setSelected(undefined)} />
    </> : null}
    <FieldLabel>Link another logged-in family member</FieldLabel>
    <Text style={styles.muted}>Generate a temporary code and share it privately. They enter it during onboarding; no email or member ID is needed.</Text>
    <ActionButton title={generate.isPending ? "Generating code..." : "Generate household code"} disabled={generate.isPending} onPress={() => void generate.mutateAsync()} />
    {joinCode ? <Text style={styles.card}>Share this code: {joinCode}</Text> : null}
    <ActionButton title="Refresh" secondary onPress={() => void q.refetch()} />
  </Screen>;
}
