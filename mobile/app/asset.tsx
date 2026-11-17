import { useState } from "react";
import { Text, TextInput } from "react-native";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Asset() {
  const id = useHousehold((s) => s.householdId); const members = useQuery({ queryKey: ["members", id], queryFn: () => api.members(id!), enabled: !!id });
  const [name, setName] = useState(""); const [category, setCategory] = useState("real_estate"); const [value, setValue] = useState(""); const [memberId, setMemberId] = useState(""); const [message, setMessage] = useState("");
  const save = useMutation({ mutationFn: () => api.createAsset(id!, { name: name.trim(), category, member_id: memberId || null, current_value: value || null, ownership_percentage: 100, valuation_date: new Date().toISOString().slice(0, 10) }), onSuccess: () => { setMessage("Asset saved."); setName(""); setValue(""); } });
  return <Screen><Text style={styles.title}>Add asset</Text><State loading={members.isLoading} error={(members.error || save.error) as Error | null} /><FieldLabel>Name</FieldLabel><TextInput style={styles.input} placeholder="Apartment, car, gold" value={name} onChangeText={setName} /><FieldLabel>Category</FieldLabel><TextInput style={styles.input} value={category} onChangeText={setCategory} /><FieldLabel>Current estimated value</FieldLabel><TextInput style={styles.input} keyboardType="decimal-pad" placeholder="0" value={value} onChangeText={setValue} /><FieldLabel>Owner</FieldLabel><TextInput style={styles.input} placeholder="Member ID (optional)" value={memberId} onChangeText={setMemberId} /><ActionButton title={save.isPending ? "Saving..." : "Save asset"} disabled={!id || !name.trim() || save.isPending} onPress={() => void save.mutateAsync()} />{message ? <Text style={styles.card}>{message}</Text> : null}</Screen>;
}
