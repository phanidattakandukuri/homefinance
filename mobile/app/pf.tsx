import { useEffect, useState } from "react";
import { Button, Text, TextInput } from "react-native";
import { Screen, styles } from "@/components/Screen";
import { api, PFAccount } from "@/lib/api";
import { useHousehold } from "@/lib/household";
import { useAuth } from "@/lib/auth";

export default function PF() {
  const id = useHousehold((state) => state.householdId);
  const user = useAuth((state) => state.user);
  const [accounts, setAccounts] = useState<PFAccount[]>([]);
  const [memberId, setMemberId] = useState("");
  const [balance, setBalance] = useState("");
  const [message, setMessage] = useState(""); const [employee, setEmployee] = useState(""); const [employer, setEmployer] = useState(""); const [eps, setEps] = useState("");
  useEffect(() => { if (id) void api.pfAccounts(id).then(setAccounts).catch((error: Error) => setMessage(error.message)); }, [id]);
  useEffect(() => { if (!id || !user?.id) return; void api.members(id).then((members) => { const current = members.find((member) => member.user_id === user.id && member.membership_status === "active"); if (current) setMemberId(current.id); }).catch(() => undefined); }, [id, user?.id]);
  async function create() { if (!id || !memberId.trim() || !balance.trim()) return; const item = await api.createPFAccount(id, { member_id: memberId.trim(), scheme: "EPF", opening_balance: balance, current_balance: balance }); setAccounts([...accounts, item]); setMessage("EPF account saved."); }
  async function addEntry(accountId: string) { if (!id) return; await api.createPFEntry(id, accountId, { entry_date: new Date().toISOString().slice(0, 10), entry_type: "contribution", employee_contribution: employee || "0", employer_contribution: employer || "0", eps_contribution: eps || "0", interest_credited: "0", withdrawal: "0" }); setMessage("PF contribution recorded."); }
  return <Screen><Text style={styles.title}>Provident Fund</Text>{accounts.map((account) => <Text style={styles.card} key={account.id}>{account.scheme}{"\n"}Balance: {account.current_balance ?? account.opening_balance}<Button title="Record contribution" onPress={() => void addEntry(account.id)}/></Text>)}<Text style={styles.muted}>Your linked household profile is used automatically.</Text><TextInput style={styles.input} placeholder="Opening/current balance" keyboardType="decimal-pad" value={balance} onChangeText={setBalance}/><Button title="Add EPF account" onPress={() => void create()} disabled={!memberId || !balance.trim()}/><TextInput style={styles.input} placeholder="Employee contribution" keyboardType="decimal-pad" value={employee} onChangeText={setEmployee}/><TextInput style={styles.input} placeholder="Employer contribution" keyboardType="decimal-pad" value={employer} onChangeText={setEmployer}/><TextInput style={styles.input} placeholder="EPS contribution" keyboardType="decimal-pad" value={eps} onChangeText={setEps}/>{message ? <Text style={styles.card}>{message}</Text> : null}</Screen>;
}
