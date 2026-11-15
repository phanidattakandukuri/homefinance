import { router } from "expo-router";
import { Text } from "react-native";
import { ActionButton, Screen, styles } from "@/components/Screen";

export default function Unavailable() {
  return (
    <Screen>
      <Text style={styles.title}>Not enabled yet</Text>

      <Text style={styles.muted}>
        This action is not connected because the backend workflow is not
        complete. No fake upload or success result was created.
      </Text>

      <ActionButton title="Back" onPress={() => router.back()} />
    </Screen>
  );
}
