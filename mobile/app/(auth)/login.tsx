import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { Link } from "expo-router";
import { useState } from "react";
import {
  Alert,
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

export default function LoginScreen() {
  const {
    login,
    isLoggingIn,
    error,
    clearError,
    biometricEnabled,
    authenticateWithBiometrics,
    checkBiometricSupport,
    enableBiometric,
  } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailError, setEmailError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const validate = () => {
    let valid = true;
    setEmailError("");
    setPasswordError("");

    if (!email.trim() || !email.includes("@")) {
      setEmailError("Enter a valid email address");
      valid = false;
    }
    if (!password) {
      setPasswordError("Password is required");
      valid = false;
    }
    return valid;
  };

  const handleLogin = async () => {
    clearError();
    if (!validate()) return;

    try {
      await login({ email: email.trim(), password });
    } catch {
      // Error surfaced via hook
    }
  };

  const handleBiometricLogin = async () => {
    const supported = await checkBiometricSupport();
    if (!supported) {
      Alert.alert(
        "Biometrics unavailable",
        "Enable Face ID or fingerprint on your device to use this feature.",
      );
      return;
    }

    const success = await authenticateWithBiometrics();
    if (success && biometricEnabled) {
      await handleLogin();
    } else if (success && !biometricEnabled) {
      try {
        await enableBiometric();
        Alert.alert("Biometrics enabled", "You can now unlock EstateOS with biometrics.");
      } catch (err) {
        Alert.alert(
          "Setup failed",
          err instanceof Error ? err.message : "Could not enable biometrics.",
        );
      }
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
        contentContainerStyle={{
          flexGrow: 1,
          justifyContent: "center",
          padding: 24,
        }}
        keyboardShouldPersistTaps="handled"
      >
        <View style={{ alignItems: "center", marginBottom: 32 }}>
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
          <Text
            style={{
              fontSize: 22,
              fontWeight: "600",
              color: colors.light.foreground,
              marginTop: 12,
            }}
          >
            EstateOS
          </Text>
        </View>

        <Card>
          <CardHeader>
            <CardTitle>Welcome back</CardTitle>
            <CardDescription>
              Sign in to manage your estate, visitors, and community.
            </CardDescription>
          </CardHeader>

          <CardContent style={{ gap: 16 }}>
            <Input
              label="Email"
              value={email}
              onChangeText={setEmail}
              placeholder="you@example.com"
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              error={emailError}
            />
            <Input
              label="Password"
              value={password}
              onChangeText={setPassword}
              placeholder="Enter your password"
              secureTextEntry
              autoComplete="password"
              error={passwordError}
            />
            {error ? (
              <Text style={{ color: colors.light.destructive, fontSize: 14 }}>
                {error}
              </Text>
            ) : null}
          </CardContent>

          <CardFooter style={{ flexDirection: "column", gap: 12 }}>
            <Button
              title="Sign in"
              onPress={handleLogin}
              loading={isLoggingIn}
              style={{ width: "100%" }}
            />
            <Pressable
              onPress={handleBiometricLogin}
              style={{
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                paddingVertical: 8,
              }}
            >
              <Ionicons
                name="finger-print"
                size={20}
                color={colors.light.primary}
              />
              <Text style={{ color: colors.light.primary, fontWeight: "500" }}>
                {biometricEnabled ? "Unlock with biometrics" : "Enable biometrics"}
              </Text>
            </Pressable>
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
            Don&apos;t have an account?
          </Text>
          <Link href="/(auth)/register" asChild>
            <Pressable>
              <Text style={{ color: colors.light.primary, fontWeight: "600" }}>
                Register
              </Text>
            </Pressable>
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
