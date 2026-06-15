import { Text, View } from "react-native";

import { colors, radius } from "@/constants/theme";

type BadgeVariant = "default" | "success" | "warning" | "destructive" | "info" | "outline";

interface BadgeProps {
  label: string;
  variant?: BadgeVariant;
}

const variantStyles: Record<
  BadgeVariant,
  { bg: string; text: string; border?: string }
> = {
  default: { bg: colors.light.primary, text: colors.light.primaryForeground },
  success: { bg: "#DCFCE7", text: colors.light.success },
  warning: { bg: "#FEF3C7", text: colors.light.warning },
  destructive: { bg: "#FEE2E2", text: colors.light.destructive },
  info: { bg: "#E0F2FE", text: colors.light.info },
  outline: {
    bg: "transparent",
    text: colors.light.foreground,
    border: colors.light.border,
  },
};

export function Badge({ label, variant = "default" }: BadgeProps) {
  const v = variantStyles[variant];

  return (
    <View
      style={{
        paddingHorizontal: 10,
        paddingVertical: 4,
        borderRadius: radius.full,
        backgroundColor: v.bg,
        borderWidth: v.border ? 1 : 0,
        borderColor: v.border,
        alignSelf: "flex-start",
      }}
    >
      <Text
        style={{
          fontSize: 12,
          fontWeight: "600",
          color: v.text,
        }}
      >
        {label}
      </Text>
    </View>
  );
}
