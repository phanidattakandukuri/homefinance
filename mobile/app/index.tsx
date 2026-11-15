import { Redirect } from "expo-router";
import { ActivityIndicator } from "react-native";
import { useAuth } from "@/lib/auth";

export default function Index() {
  const { hydrated, user } = useAuth();
  if (!hydrated) return <ActivityIndicator accessibilityLabel="Loading" />;
  return <Redirect href={user ? "/(tabs)" : "/welcome"} />;
}
