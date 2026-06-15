import { LinearGradient } from "expo-linear-gradient";
import { Link } from "expo-router";
import { useState } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  Text,
  View,
} from "react-native";

import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Input,
} from "@/components";
import { colors, radius } from "@/constants/theme";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterScreen() {
  const { register, isRegistering, error, clearError } = useAuth();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    password: "",
    password_confirm: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const update = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: "" }));
  };

  const validate = () => {
    const next: Record<string, string> = {};
    if (!form.first_name.trim()) next.first_name = "First name is required";
    if (!form.last_name.trim()) next.last_name = "Last name is required";
    if (!form.email.includes("@")) next.email = "Enter a valid email";
    if (form.password.length < 8) next.password = "Minimum 8 characters";
    if (form.password !== form.password_confirm) {
      next.password_confirm = "Passwords do not match";
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleRegister = async () => {
    clearError();
    if (!validate()) return;

    try {
      await register({
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || undefined,
        password: form.password,
        password_confirm: form.password_confirm,
      });
    } catch {
      // Error surfaced via hook
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: colors.light.muted }}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <LinearGradient
        colors={[`${colors.light.primary}26`, "transparent"]}
        style={{ position: "absolute", top: 0, left: 0, right: 0, height: 300 }}
      />

      <ScrollView
        contentContainerStyle={{ padding: 24, paddingTop: 48 }}
        keyboardShouldPersistTaps="handled"
      >
        <View style={{ alignItems: "center", marginBottom: 24 }}>
          <LinearGradient
            colors={[colors.light.brandGradientFrom, colors.light.brandGradientTo]}
            style={{
              width: 48,
              height: 48,
              borderRadius: radius.lg,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text style={{ color: "#FFF", fontSize: 22, fontWeight: "700" }}>E</Text>
          </LinearGradient>
        </View>

        <Card>
          <CardHeader>
            <CardTitle>Create account</CardTitle>
            <CardDescription>
              Join your estate community on EstateOS.
            </CardDescription>
          </CardHeader>

          <CardContent style={{ gap: 14 }}>
            <View style={{ flexDirection: "row", gap: 12 }}>
              <View style={{ flex: 1 }}>
                <Input
                  label="First name"
                  value={form.first_name}
                  onChangeText={(v) => update("first_name", v)}
                  error={errors.first_name}
                />
              </View>
              <View style={{ flex: 1 }}>
                <Input
                  label="Last name"
                  value={form.last_name}
                  onChangeText={(v) => update("last_name", v)}
                  error={errors.last_name}
                />
              </View>
            </View>
            <Input
              label="Email"
              value={form.email}
              onChangeText={(v) => update("email", v)}
              keyboardType="email-address"
              autoCapitalize="none"
              error={errors.email}
            />
            <Input
              label="Phone (optional)"
              value={form.phone}
              onChangeText={(v) => update("phone", v)}
              keyboardType="phone-pad"
            />
            <Input
              label="Password"
              value={form.password}
              onChangeText={(v) => update("password", v)}
              secureTextEntry
              error={errors.password}
            />
            <Input
              label="Confirm password"
              value={form.password_confirm}
              onChangeText={(v) => update("password_confirm", v)}
              secureTextEntry
              error={errors.password_confirm}
            />
            {error ? (
              <Text style={{ color: colors.light.destructive, fontSize: 14 }}>
                {error}
              </Text>
            ) : null}
          </CardContent>

          <CardFooter>
            <Button
              title="Create account"
              onPress={handleRegister}
              loading={isRegistering}
              style={{ flex: 1 }}
            />
          </CardFooter>
        </Card>

        <View
          style={{
            flexDirection: "row",
            justifyContent: "center",
            marginTop: 24,
            gap: 4,
          }}
        >
          <Text style={{ color: colors.light.mutedForeground }}>
            Already have an account?
          </Text>
          <Link href="/(auth)/login" asChild>
            <Pressable>
              <Text style={{ color: colors.light.primary, fontWeight: "600" }}>
                Sign in
              </Text>
            </Pressable>
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
