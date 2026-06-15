import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { Alert, Pressable, ScrollView, Switch, Text, View } from "react-native";

import { Avatar, Button, Card, CardContent, Header } from "@/components";
import { colors, radius } from "@/constants/theme";
import { useAuth } from "@/hooks/useAuth";
import { useNotifications } from "@/hooks/useNotifications";
import { useEstateStore } from "@/stores/estate";

export default function ProfileScreen() {
  const router = useRouter();
  const { user, logout, biometricEnabled, enableBiometric, disableBiometric } =
    useAuth();
  const { currentEstate } = useEstateStore();
  const { isGranted, requestPermission } = useNotifications();

  const handleBiometricToggle = async (value: boolean) => {
    try {
      if (value) {
        await enableBiometric();
      } else {
        disableBiometric();
      }
    } catch (err) {
      Alert.alert(
        "Biometrics",
        err instanceof Error ? err.message : "Could not update biometric settings.",
      );
    }
  };

  const settings = [
    {
      icon: "notifications" as const,
      label: "Push notifications",
      action: (
        <Switch
          value={isGranted}
          onValueChange={(value) => {
            if (value) void requestPermission();
          }}
          trackColor={{ true: colors.light.primary }}
        />
      ),
    },
    {
      icon: "finger-print" as const,
      label: "Biometric unlock",
      action: (
        <Switch
          value={biometricEnabled}
          onValueChange={handleBiometricToggle}
          trackColor={{ true: colors.light.primary }}
        />
      ),
    },
    {
      icon: "shield-checkmark" as const,
      label: "Gate scanner",
      action: (
        <Pressable onPress={() => router.push("/visitors/scan")}>
          <Ionicons name="chevron-forward" size={20} color={colors.light.mutedForeground} />
        </Pressable>
      ),
    },
  ];

  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header title="Profile" />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 16 }}>
        <Card>
          <CardContent
            style={{
              flexDirection: "row",
              alignItems: "center",
              gap: 16,
            }}
          >
            <Avatar
              src={user?.avatar}
              name={`${user?.first_name ?? ""} ${user?.last_name ?? ""}`}
              size={64}
            />
            <View style={{ flex: 1, gap: 4 }}>
              <Text
                style={{
                  fontSize: 18,
                  fontWeight: "600",
                  color: colors.light.foreground,
                }}
              >
                {user?.first_name} {user?.last_name}
              </Text>
              <Text style={{ color: colors.light.mutedForeground, fontSize: 14 }}>
                {user?.email}
              </Text>
              {currentEstate ? (
                <Text style={{ color: colors.light.primary, fontSize: 13 }}>
                  {currentEstate.name}
                </Text>
              ) : null}
            </View>
          </CardContent>
        </Card>

        <Card>
          <CardContent style={{ gap: 0 }}>
            {settings.map((item, index) => (
              <View
                key={item.label}
                style={{
                  flexDirection: "row",
                  alignItems: "center",
                  paddingVertical: 14,
                  borderTopWidth: index > 0 ? 1 : 0,
                  borderTopColor: colors.light.border,
                  gap: 12,
                }}
              >
                <View
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: radius.md,
                    backgroundColor: colors.light.accent,
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Ionicons name={item.icon} size={18} color={colors.light.primary} />
                </View>
                <Text
                  style={{
                    flex: 1,
                    fontSize: 15,
                    color: colors.light.foreground,
                  }}
                >
                  {item.label}
                </Text>
                {item.action}
              </View>
            ))}
          </CardContent>
        </Card>

        <Button title="Sign out" variant="destructive" onPress={() => logout()} />
      </ScrollView>
    </View>
  );
}
