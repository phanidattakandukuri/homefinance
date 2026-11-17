import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "@/components/Screen";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={({ route }) => ({
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.muted,
        tabBarLabelStyle: { fontWeight: "600" },
        headerStyle: { backgroundColor: colors.surface },
        headerTintColor: colors.ink,
        tabBarIcon: ({ color, size }) => {
          const icons: Record<string, keyof typeof Ionicons.glyphMap> = {
            index: "home-outline",
            activity: "list-outline",
            add: "add-circle",
            wealth: "trending-up-outline",
            profile: "person-outline",
          };
          return <Ionicons name={icons[route.name] ?? "ellipse-outline"} size={route.name === "add" ? size + 4 : size} color={typeof color === "number" ? colors.ink : color ?? colors.ink} />;
        },
      })}
    >
      <Tabs.Screen
        name="index"
        options={{ title: "Home", tabBarLabel: "Home" }}
      />
      <Tabs.Screen
        name="activity"
        options={{ title: "Activity", tabBarLabel: "Activity" }}
      />
      <Tabs.Screen name="add" options={{ title: "Add", tabBarLabel: "Add" }} />
      <Tabs.Screen
        name="wealth"
        options={{ title: "Wealth", tabBarLabel: "Wealth" }}
      />
      <Tabs.Screen
        name="profile"
        options={{ title: "Profile", tabBarLabel: "Profile" }}
      />
    </Tabs>
  );
}
