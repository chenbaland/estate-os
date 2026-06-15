import { Ionicons } from "@expo/vector-icons";
import { useMutation } from "@tanstack/react-query";
import { CameraView, useCameraPermissions } from "expo-camera";
import { useRouter } from "expo-router";
import { useState } from "react";
import { Alert, Text, View } from "react-native";

import { Badge, Button, Card, CardContent, Header } from "@/components";
import { colors, radius } from "@/constants/theme";
import { api } from "@/lib/api";
import type { VisitorPass } from "@/types";

export default function ScanVisitorScreen() {
  const router = useRouter();
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [result, setResult] = useState<VisitorPass | null>(null);

  const scanMutation = useMutation({
    mutationFn: (qrCode: string) => api.scanVisitorPass(qrCode),
    onSuccess: (pass) => {
      setResult(pass);
      setScanned(true);
    },
    onError: (err) => {
      setScanned(false);
      Alert.alert(
        "Scan failed",
        err instanceof Error ? err.message : "Invalid or expired visitor pass.",
      );
    },
  });

  if (!permission) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
        <Header title="Gate Scanner" showBack />
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <Text>Requesting camera permission...</Text>
        </View>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
        <Header title="Gate Scanner" showBack />
        <View
          style={{
            flex: 1,
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
            gap: 16,
          }}
        >
          <Ionicons name="camera" size={48} color={colors.light.mutedForeground} />
          <Text style={{ textAlign: "center", color: colors.light.mutedForeground }}>
            Camera access is required to scan visitor QR codes at the gate.
          </Text>
          <Button title="Grant permission" onPress={requestPermission} />
        </View>
      </View>
    );
  }

  if (result) {
    const isValid = result.status === "active";
    return (
      <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
        <Header title="Scan Result" showBack />
        <View style={{ padding: 24, gap: 16 }}>
          <Card>
            <CardContent style={{ gap: 12 }}>
              <View style={{ alignItems: "center", gap: 8 }}>
                <Ionicons
                  name={isValid ? "checkmark-circle" : "close-circle"}
                  size={64}
                  color={isValid ? colors.light.success : colors.light.destructive}
                />
                <Text
                  style={{
                    fontSize: 20,
                    fontWeight: "700",
                    color: colors.light.foreground,
                  }}
                >
                  {result.visitor_name}
                </Text>
                <Badge
                  label={result.status}
                  variant={isValid ? "success" : "destructive"}
                />
              </View>
              <Text style={{ color: colors.light.mutedForeground }}>
                Purpose: {result.purpose}
              </Text>
              <Text style={{ color: colors.light.mutedForeground }}>
                Phone: {result.visitor_phone}
              </Text>
              <Text style={{ color: colors.light.mutedForeground }}>
                Valid until: {new Date(result.valid_until).toLocaleString()}
              </Text>
            </CardContent>
          </Card>
          <Button
            title="Scan another"
            onPress={() => {
              setResult(null);
              setScanned(false);
            }}
          />
          <Button title="Done" variant="outline" onPress={() => router.back()} />
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: "#000" }}>
      <Header title="Gate Scanner" showBack subtitle="Scan visitor QR code" />

      <CameraView
        style={{ flex: 1 }}
        facing="back"
        barcodeScannerSettings={{ barcodeTypes: ["qr"] }}
        onBarcodeScanned={
          scanned
            ? undefined
            : ({ data }) => {
                setScanned(true);
                scanMutation.mutate(data);
              }
        }
      />

      <View
        style={{
          position: "absolute",
          bottom: 48,
          left: 24,
          right: 24,
          alignItems: "center",
          gap: 12,
        }}
      >
        <View
          style={{
            width: 240,
            height: 240,
            borderWidth: 2,
            borderColor: colors.light.primary,
            borderRadius: radius.lg,
            backgroundColor: "transparent",
          }}
        />
        <Text style={{ color: "#FFF", fontSize: 14 }}>
          {scanMutation.isPending ? "Verifying..." : "Align QR code within frame"}
        </Text>
      </View>
    </View>
  );
}
