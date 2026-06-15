import { forwardRef } from "react";
import {
  Text,
  TextInput,
  View,
  type TextInputProps,
} from "react-native";

import { colors, radius } from "@/constants/theme";

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<TextInput, InputProps>(
  ({ label, error, hint, style, ...props }, ref) => {
    return (
      <View style={{ gap: 6 }}>
        {label ? (
          <Text
            style={{
              fontSize: 14,
              fontWeight: "500",
              color: colors.light.foreground,
            }}
          >
            {label}
          </Text>
        ) : null}
        <TextInput
          ref={ref}
          placeholderTextColor={colors.light.mutedForeground}
          style={[
            {
              height: 44,
              borderWidth: 1,
              borderColor: error ? colors.light.destructive : colors.light.input,
              borderRadius: radius.md,
              paddingHorizontal: 12,
              fontSize: 16,
              color: colors.light.foreground,
              backgroundColor: colors.light.background,
            },
            style,
          ]}
          {...props}
        />
        {error ? (
          <Text style={{ fontSize: 12, color: colors.light.destructive }}>
            {error}
          </Text>
        ) : hint ? (
          <Text style={{ fontSize: 12, color: colors.light.mutedForeground }}>
            {hint}
          </Text>
        ) : null}
      </View>
    );
  },
);

Input.displayName = "Input";
