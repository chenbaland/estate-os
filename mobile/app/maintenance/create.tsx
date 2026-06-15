import { useMutation } from "@tanstack/react-query";
import { useRouter } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, ScrollView, Text, View } from "react-native";

import { Button, Header, Input } from "@/components";
import { colors, radius } from "@/constants/theme";
import { api } from "@/lib/api";

const CATEGORIES = ["Plumbing", "Electrical", "HVAC", "Structural", "Other"];
const PRIORITIES = ["low", "medium", "high", "urgent"] as const;

export default function CreateMaintenanceScreen() {
  const router = useRouter();
  const [form, setForm] = useState({
    title: "",
    description: "",
    category: "Plumbing",
    priority: "medium" as (typeof PRIORITIES)[number],
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createMutation = useMutation({
    mutationFn: () =>
      api.createMaintenanceRequest({
        title: form.title.trim(),
        description: form.description.trim(),
        category: form.category,
        priority: form.priority,
      }),
    onSuccess: () => {
      Alert.alert("Submitted", "Your maintenance request has been logged.", [
        { text: "OK", onPress: () => router.back() },
      ]);
    },
    onError: (err) => {
      Alert.alert(
        "Error",
        err instanceof Error ? err.message : "Could not submit request.",
      );
    },
  });

  const validate = () => {
    const next: Record<string, string> = {};
    if (!form.title.trim()) next.title = "Title is required";
    if (!form.description.trim()) next.description = "Description is required";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = () => {
    if (!validate()) return;
    createMutation.mutate();
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header title="Maintenance Request" showBack />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 16 }}>
        <Input
          label="Title"
          value={form.title}
          onChangeText={(v) => setForm((p) => ({ ...p, title: v }))}
          placeholder="Brief summary of the issue"
          error={errors.title}
        />
        <Input
          label="Description"
          value={form.description}
          onChangeText={(v) => setForm((p) => ({ ...p, description: v }))}
          placeholder="Describe the problem in detail..."
          multiline
          style={{ minHeight: 120, textAlignVertical: "top" }}
          error={errors.description}
        />

        <Text style={{ fontSize: 14, fontWeight: "500", color: colors.light.foreground }}>
          Category
        </Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
          {CATEGORIES.map((cat) => (
            <Pressable
              key={cat}
              onPress={() => setForm((p) => ({ ...p, category: cat }))}
              style={{
                paddingHorizontal: 14,
                paddingVertical: 8,
                borderRadius: radius.full,
                backgroundColor:
                  form.category === cat ? colors.light.primary : colors.light.secondary,
              }}
            >
              <Text
                style={{
                  color:
                    form.category === cat
                      ? colors.light.primaryForeground
                      : colors.light.secondaryForeground,
                  fontWeight: "500",
                  fontSize: 13,
                }}
              >
                {cat}
              </Text>
            </Pressable>
          ))}
        </View>

        <Text style={{ fontSize: 14, fontWeight: "500", color: colors.light.foreground }}>
          Priority
        </Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
          {PRIORITIES.map((p) => (
            <Pressable
              key={p}
              onPress={() => setForm((prev) => ({ ...prev, priority: p }))}
              style={{
                paddingHorizontal: 14,
                paddingVertical: 8,
                borderRadius: radius.full,
                backgroundColor:
                  form.priority === p ? colors.light.primary : colors.light.secondary,
              }}
            >
              <Text
                style={{
                  color:
                    form.priority === p
                      ? colors.light.primaryForeground
                      : colors.light.secondaryForeground,
                  fontWeight: "500",
                  fontSize: 13,
                  textTransform: "capitalize",
                }}
              >
                {p}
              </Text>
            </Pressable>
          ))}
        </View>

        <Button
          title="Submit request"
          onPress={handleSubmit}
          loading={createMutation.isPending}
        />
      </ScrollView>
    </View>
  );
}
