import { useState } from "react";
import { Pressable, Text, TextInput } from "react-native";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api, Member } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Members() {
  const id = useHousehold((s) => s.householdId);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [selected, setSelected] = useState<Member>();
  const [editName, setEditName] = useState("");
  const [occupation, setOccupation] = useState("");
  const q = useQuery({ queryKey: ["members", id], queryFn: () => api.members(id!), enabled: !!id });
  const invite = useMutation({
    mutationFn: () => api.inviteMember(id!, { display_name: name.trim(), email: email.trim() }),
    onSuccess: (result) => { setToken(result.invitation_token); setName(""); setEmail(""); void q.refetch(); },
  });
  const update = useMutation({
    mutationFn: () => api.updateMember(id!, selected!.id, { display_name: editName.trim(), occupation: occupation.trim() || null }),
    onSuccess: () => { setSelected(undefined); void q.refetch(); },
  });
  function selectMember(member: Member) { setSelected(member); setEditName(member.display_name); setOccupation(member.occupation ?? ""); }
  return <Screen>
    <Text style={styles.title}>Household members</Text>
    <State loading={q.isLoading} error={(q.error || invite.error || update.error) as Error | null} />
    {q.data?.map((member) => <Pressable key={member.id} onPress={() => selectMember(member)}><Text style={styles.card}>{member.display_name} — {member.role} · {member.membership_status}{member.user_id ? " · linked" : " · pending"}</Text></Pressable>)}
    {selected ? <>
      <FieldLabel>Edit member profile</FieldLabel>
      <TextInput style={styles.input} placeholder="Full name" value={editName} onChangeText={setEditName} />
      <TextInput style={styles.input} placeholder="Occupation" value={occupation} onChangeText={setOccupation} />
      <ActionButton title={update.isPending ? "Saving..." : "Save member"} disabled={!editName.trim() || update.isPending} onPress={() => void update.mutateAsync()} />
      <ActionButton title="Cancel" secondary onPress={() => setSelected(undefined)} />
    </> : null}
    <FieldLabel>Invite a family member</FieldLabel>
    <TextInput style={styles.input} placeholder="Full name" value={name} onChangeText={setName} />
    <TextInput style={styles.input} placeholder="Email address" autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} />
    <ActionButton title={invite.isPending ? "Creating invitation..." : "Create invitation"} disabled={!name.trim() || !email.trim() || invite.isPending} onPress={() => void invite.mutateAsync()} />
    {token ? <Text style={styles.card}>Invitation created. Share this one-time setup token securely: {token}</Text> : null}
    <ActionButton title="Refresh" secondary onPress={() => void q.refetch()} />
  </Screen>;
}
