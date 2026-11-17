import { useEffect, useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";
import { useAuth } from "@/lib/auth";

export default function Asset() {
  const id = useHousehold((s) => s.householdId); const user = useAuth((s) => s.user); const members = useQuery({ queryKey: ["members", id], queryFn: () => api.members(id!), enabled: !!id });
  const [name, setName] = useState(""); const [category, setCategory] = useState("real_estate"); const [value, setValue] = useState(""); const [memberId, setMemberId] = useState(""); const [message, setMessage] = useState("");
  const assetCategories = ["real_estate", "vehicle", "gold", "cash", "electronics", "other"];
  useEffect(() => { const current = members.data?.find((member) => member.user_id === user?.id && member.membership_status === "active"); if (current && !memberId) setMemberId(current.id); }, [members.data, user?.id, memberId]);
  const save = useMutation({ mutationFn: () => api.createAsset(id!, { name: name.trim(), category, member_id: memberId || null, current_value: value || null, ownership_percentage: 100, valuation_date: new Date().toISOString().slice(0, 10) }), onSuccess: () => { setMessage("Asset saved."); setName(""); setValue(""); } });
  return <Screen><Text style={styles.title}>Add asset</Text><State loading={members.isLoading} error={(members.error || save.error) as Error | null} /><FieldLabel>Name</FieldLabel><TextInput style={styles.input} placeholder="Apartment, car, gold" value={name} onChangeText={setName} /><FieldLabel>Category</FieldLabel><View style={styles.chipRow}>{assetCategories.map((item) => <Pressable key={item} onPress={() => setCategory(item)} style={[styles.chip, category === item && styles.selectedChip]}><Text style={styles.chipText}>{item.replace("_", " ")}</Text></Pressable>)}</View><FieldLabel>Current estimated value</FieldLabel><TextInput style={styles.input} keyboardType="decimal-pad" placeholder="0" value={value} onChangeText={setValue} /><Text style={styles.muted}>Owner is automatically set to your linked household profile.</Text><ActionButton title={save.isPending ? "Saving..." : "Save asset"} disabled={!id || !memberId || !name.trim() || save.isPending} onPress={() => void save.mutateAsync()} />{message ? <Text style={styles.card}>{message}</Text> : null}</Screen>;
}
