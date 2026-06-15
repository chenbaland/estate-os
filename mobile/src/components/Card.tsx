import { View, Text, type ViewProps } from "react-native";

import { colors, radius, shadows } from "@/constants/theme";

interface CardProps extends ViewProps {
  children: React.ReactNode;
}

export function Card({ children, style, ...props }: CardProps) {
  return (
    <View
      style={[
        {
          backgroundColor: colors.light.card,
          borderRadius: radius.lg,
          borderWidth: 1,
          borderColor: colors.light.border,
          ...shadows.sm,
        },
        style,
      ]}
      {...props}
    >
      {children}
    </View>
  );
}

interface CardHeaderProps extends ViewProps {
  children: React.ReactNode;
}

export function CardHeader({ children, style, ...props }: CardHeaderProps) {
  return (
    <View style={[{ padding: 16, paddingBottom: 8 }, style]} {...props}>
      {children}
    </View>
  );
}

interface CardTitleProps {
  children: string;
}

export function CardTitle({ children }: CardTitleProps) {
  return (
    <Text
      style={{
        fontSize: 18,
        fontWeight: "600",
        color: colors.light.cardForeground,
      }}
    >
      {children}
    </Text>
  );
}

interface CardDescriptionProps {
  children: string;
}

export function CardDescription({ children }: CardDescriptionProps) {
  return (
    <Text
      style={{
        fontSize: 14,
        color: colors.light.mutedForeground,
        marginTop: 4,
      }}
    >
      {children}
    </Text>
  );
}

interface CardContentProps extends ViewProps {
  children: React.ReactNode;
}

export function CardContent({ children, style, ...props }: CardContentProps) {
  return (
    <View style={[{ padding: 16, paddingTop: 8 }, style]} {...props}>
      {children}
    </View>
  );
}

interface CardFooterProps extends ViewProps {
  children: React.ReactNode;
}

export function CardFooter({ children, style, ...props }: CardFooterProps) {
  return (
    <View
      style={[
        {
          padding: 16,
          paddingTop: 8,
          flexDirection: "row",
          alignItems: "center",
          gap: 8,
        },
        style,
      ]}
      {...props}
    >
      {children}
    </View>
  );
}
