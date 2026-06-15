import {
  ActivityIndicator,
  Pressable,
  Text,
  type PressableProps,
  type StyleProp,
  type ViewStyle,
} from "react-native";

import { colors, radius } from "@/constants/theme";

type ButtonVariant = "default" | "destructive" | "outline" | "secondary" | "ghost";
type ButtonSize = "default" | "sm" | "lg";

interface ButtonProps extends Omit<PressableProps, "style"> {
  title: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: React.ReactNode;
  style?: StyleProp<ViewStyle>;
}

const variantStyles: Record<
  ButtonVariant,
  { bg: string; text: string; border?: string }
> = {
  default: { bg: colors.light.primary, text: colors.light.primaryForeground },
  destructive: {
    bg: colors.light.destructive,
    text: colors.light.destructiveForeground,
  },
  outline: {
    bg: "transparent",
    text: colors.light.foreground,
    border: colors.light.border,
  },
  secondary: {
    bg: colors.light.secondary,
    text: colors.light.secondaryForeground,
  },
  ghost: { bg: "transparent", text: colors.light.primary },
};

const sizeStyles: Record<ButtonSize, { height: number; px: number; fontSize: number }> = {
  default: { height: 44, px: 16, fontSize: 14 },
  sm: { height: 36, px: 12, fontSize: 13 },
  lg: { height: 48, px: 24, fontSize: 16 },
};

export function Button({
  title,
  variant = "default",
  size = "default",
  loading = false,
  disabled,
  icon,
  style,
  ...props
}: ButtonProps) {
  const v = variantStyles[variant];
  const s = sizeStyles[size];
  const isDisabled = disabled || loading;

  return (
    <Pressable
      disabled={isDisabled}
      style={({ pressed }) => [
        {
          height: s.height,
          paddingHorizontal: s.px,
          borderRadius: radius.md,
          backgroundColor: v.bg,
          borderWidth: v.border ? 1 : 0,
          borderColor: v.border,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          opacity: isDisabled ? 0.5 : pressed ? 0.9 : 1,
        },
        style,
      ]}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color={v.text} size="small" />
      ) : (
        <>
          {icon}
          <Text
            style={{
              color: v.text,
              fontSize: s.fontSize,
              fontWeight: "600",
            }}
          >
            {title}
          </Text>
        </>
      )}
    </Pressable>
  );
}
