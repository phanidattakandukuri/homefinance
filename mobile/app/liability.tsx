import { useState } from "react";
import { Text, TextInput } from "react-native";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ActionButton, FieldLabel, Screen, State, styles } from "@/components/Screen";
import { api } from "@/lib/api";
import { useHousehold } from "@/lib/household";

export default function Liability() {
  const id = useHousehold((s) => s.householdId); const members = useQuery({ queryKey: ["members", id], queryFn: () => api.members(id!), enabled: !!id });
  const [name, setName] = useState(""); const [category, setCategory] = useState("home_loan"); const [outstanding, setOutstanding] = useState(""); const [rate, setRate] = useState(""); const [emi, setEmi] = useState(""); const [memberId, setMemberId] = useState(""); const [message, setMessage] = useState("");
  const save = useMutation({ mutationFn: () => api.createLiability(id!, { name: name.trim(), category, member_id: memberId || null, current_outstanding: outstanding || null, interest_rate: rate || null, emi: emi || null, interest_type: "fixed", emi_frequency: "monthly" }), onSuccess: () => { setMessage("Liability saved."); setName(""); setOutstanding(""); setRate(""); setEmi(""); } });
  return <Screen><Text style={styles.title}>Add loan or liability</Text><State loading={members.isLoading} error={(members.error || save.error) as Error | null} /><FieldLabel>Name</FieldLabel><TextInput style={styles.input} placeholder="Home loan, credit card" value={name} onChangeText={setName} /><FieldLabel>Type</FieldLabel><TextInput style={styles.input} value={category} onChangeText={setCategory} /><FieldLabel>Outstanding principal</FieldLabel><TextInput style={styles.input} keyboardType="decimal-pad" value={outstanding} onChangeText={setOutstanding} /><FieldLabel>Annual interest rate (%)</FieldLabel><TextInput style={styles.input} keyboardType="decimal-pad" value={rate} onChangeText={setRate} /><FieldLabel>EMI amount</FieldLabel><TextInput style={styles.input} keyboardType="decimal-pad" value={emi} onChangeText={setEmi} /><FieldLabel>Borrower member ID (optional)</FieldLabel><TextInput style={styles.input} value={memberId} onChangeText={setMemberId} /><ActionButton title={save.isPending ? "Saving..." : "Save liability"} disabled={!id || !name.trim() || save.isPending} onPress={() => void save.mutateAsync()} />{message ? <Text style={styles.card}>{message}</Text> : null}</Screen>;
}
