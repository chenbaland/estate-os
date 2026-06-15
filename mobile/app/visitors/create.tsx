import { useMutation } from "@tanstack/react-query";
import { useRouter } from "expo-router";
import { useState } from "react";
import { Alert, ScrollView, Text, View } from "react-native";
import QRCode from "react-native-qrcode-svg";

import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Header,
  Input,
} from "@/components";
import { colors } from "@/constants/theme";
import { api } from "@/lib/api";
import type { VisitorPass } from "@/types";

export default function CreateVisitorScreen() {
  const router = useRouter();
  const [form, setForm] = useState({
    visitor_name: "",
    visitor_phone: "",
    purpose: "",
    valid_hours: "4",
  });
  const [createdPass, setCreatedPass] = useState<VisitorPass | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createMutation = useMutation({
    mutationFn: () => {
      const hours = parseInt(form.valid_hours, 10) || 4;
      const validUntil = new Date(Date.now() + hours * 60 * 60 * 1000).toISOString();
      return api.createVisitorPass({
        visitor_name: form.visitor_name.trim(),
        visitor_phone: form.visitor_phone.trim(),
        purpose: form.purpose.trim(),
        valid_until: validUntil,
      });
    },
    onSuccess: (pass) => {
      setCreatedPass(pass);
    },
    onError: (err) => {
      Alert.alert(
        "Error",
        err instanceof Error ? err.message : "Could not create visitor pass.",
      );
    },
  });

  const validate = () => {
    const next: Record<string, string> = {};
    if (!form.visitor_name.trim()) next.visitor_name = "Visitor name is required";
    if (!form.visitor_phone.trim()) next.visitor_phone = "Phone number is required";
    if (!form.purpose.trim()) next.purpose = "Purpose is required";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleCreate = () => {
    if (!validate()) return;
    createMutation.mutate();
  };

  if (createdPass) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
        <Header title="Visitor Pass" showBack />
        <ScrollView contentContainerStyle={{ padding: 24, alignItems: "center", gap: 24 }}>
          <Card style={{ width: "100%" }}>
            <CardHeader>
              <CardTitle>{createdPass.visitor_name}</CardTitle>
            </CardHeader>
            <CardContent style={{ alignItems: "center", gap: 16 }}>
              <QRCode value={createdPass.qr_code} size={200} />
              <Text style={{ color: colors.light.mutedForeground, textAlign: "center" }}>
                Show this QR code at the gate for entry. Valid until{" "}
                {new Date(createdPass.valid_until).toLocaleString()}.
              </Text>
            </CardContent>
          </Card>
          <Button title="Done" onPress={() => router.back()} style={{ width: "100%" }} />
        </ScrollView>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header title="Create Visitor Pass" showBack />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 16 }}>
        <Input
          label="Visitor name"
          value={form.visitor_name}
          onChangeText={(v) => setForm((p) => ({ ...p, visitor_name: v }))}
          placeholder="Full name"
          error={errors.visitor_name}
        />
        <Input
          label="Phone number"
          value={form.visitor_phone}
          onChangeText={(v) => setForm((p) => ({ ...p, visitor_phone: v }))}
          placeholder="+234..."
          keyboardType="phone-pad"
          error={errors.visitor_phone}
        />
        <Input
          label="Purpose of visit"
          value={form.purpose}
          onChangeText={(v) => setForm((p) => ({ ...p, purpose: v }))}
          placeholder="e.g. Family visit, delivery"
          error={errors.purpose}
        />
        <Input
          label="Valid for (hours)"
          value={form.valid_hours}
          onChangeText={(v) => setForm((p) => ({ ...p, valid_hours: v }))}
          keyboardType="number-pad"
          hint="Default is 4 hours"
        />

        <Button
          title="Generate QR Pass"
          onPress={handleCreate}
          loading={createMutation.isPending}
        />
      </ScrollView>
    </View>
  );
}
