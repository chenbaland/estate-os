import { Ionicons } from "@expo/vector-icons";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "expo-router";
import { useState } from "react";
import { Alert, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { Button, Input } from "@/components";
import { colors, radius } from "@/constants/theme";
import { api } from "@/lib/api";

export default function SOSScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [message, setMessage] = useState("");
  const [sent, setSent] = useState(false);

  const sosMutation = useMutation({
    mutationFn: () =>
      api.triggerSOS({
        message: message.trim() || "Emergency SOS triggered from mobile app",
      }),
    onSuccess: () => {
      setSent(true);
      Alert.alert(
        "SOS Sent",
        "Security and emergency contacts have been notified. Help is on the way.",
        [{ text: "OK", onPress: () => router.back() }],
      );
    },
    onError: (err) => {
      Alert.alert(
        "SOS Failed",
        err instanceof Error ? err.message : "Could not send SOS. Call emergency services.",
      );
    },
  });

  return (
    <View
      style={{
        flex: 1,
        backgroundColor: colors.light.destructive,
        paddingTop: insets.top + 16,
        paddingBottom: insets.bottom + 24,
        paddingHorizontal: 24,
      }}
    >
      <Button
        title="Cancel"
        variant="ghost"
        onPress={() => router.back()}
        style={{ alignSelf: "flex-start", marginBottom: 24 }}
      />

      <View style={{ flex: 1, alignItems: "center", justifyContent: "center", gap: 24 }}>
        <View
          style={{
            width: 120,
            height: 120,
            borderRadius: radius.full,
            backgroundColor: "rgba(255,255,255,0.2)",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Ionicons name="warning" size={64} color="#FFF" />
        </View>

        <Text
          style={{
            fontSize: 28,
            fontWeight: "700",
            color: "#FFF",
            textAlign: "center",
          }}
        >
          Emergency SOS
        </Text>
        <Text
          style={{
            fontSize: 16,
            color: "rgba(255,255,255,0.9)",
            textAlign: "center",
            lineHeight: 24,
          }}
        >
          Press the button below to alert estate security and emergency responders
          immediately.
        </Text>

        <View style={{ width: "100%", marginTop: 16 }}>
          <Input
            label="Additional details (optional)"
            value={message}
            onChangeText={setMessage}
            placeholder="Describe the emergency..."
            multiline
            style={{ minHeight: 80, textAlignVertical: "top" }}
          />
        </View>
      </View>

      <Button
        title={sent ? "SOS Sent" : "Send SOS Alert"}
        onPress={() => sosMutation.mutate()}
        loading={sosMutation.isPending}
        disabled={sent}
        style={{
          backgroundColor: "#FFF",
          height: 56,
        }}
      />
      <Text
        style={{
          color: "rgba(255,255,255,0.8)",
          textAlign: "center",
          marginTop: 12,
          fontSize: 13,
        }}
      >
        Your location and unit info will be shared with security.
      </Text>
    </View>
  );
}
