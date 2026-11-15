import { Tabs } from "expo-router";
import { colors } from "@/components/Screen";

export default function TabLayout() {
  return <Tabs screenOptions={{ tabBarActiveTintColor: colors.primary, tabBarLabelStyle: { fontWeight: "600" }, headerStyle: { backgroundColor: colors.surface }, headerTintColor: colors.ink }}>
    <Tabs.Screen name="index" options={{ title: "Home", tabBarLabel: "Home" }} />
    <Tabs.Screen name="activity" options={{ title: "Activity", tabBarLabel: "Activity" }} />
    <Tabs.Screen name="add" options={{ title: "Add", tabBarLabel: "Add" }} />
    <Tabs.Screen name="wealth" options={{ title: "Wealth", tabBarLabel: "Wealth" }} />
    <Tabs.Screen name="profile" options={{ title: "Profile", tabBarLabel: "Profile" }} />
  </Tabs>;
}
