import { QueryClientProvider } from "@tanstack/react-query";
import { Stack } from "expo-router";
import { useEffect } from "react";
import { queryClient } from "@/lib/query";
import { useAuth } from "@/lib/auth";
import { useHousehold } from "@/lib/household";
import { initOffline } from "@/lib/offline";
import { syncQueue } from "@/lib/offline";
import { enableNotifications } from "@/lib/notifications";

export default function Layout() {
  const hydrate = useAuth((state) => state.hydrate);
  const hydrateHousehold = useHousehold((state) => state.hydrate);
  const householdId = useHousehold((state) => state.householdId);
  useEffect(() => { void hydrate(); void hydrateHousehold(); void initOffline(); void enableNotifications(); }, [hydrate, hydrateHousehold]);
  useEffect(() => { if (!householdId) return; const timer = setInterval(() => { void syncQueue(householdId); }, 15000); void syncQueue(householdId); return () => clearInterval(timer); }, [householdId]);
  return <QueryClientProvider client={queryClient}><Stack screenOptions={{ headerShown: false }} /></QueryClientProvider>;
}
