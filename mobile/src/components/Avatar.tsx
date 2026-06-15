import { Image, Text, View } from "react-native";

import { colors, radius } from "@/constants/theme";

interface AvatarProps {
  src?: string | null;
  name?: string;
  size?: number;
}

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

export function Avatar({ src, name = "?", size = 40 }: AvatarProps) {
  if (src) {
    return (
      <Image
        source={{ uri: src }}
        style={{
          width: size,
          height: size,
          borderRadius: radius.full,
        }}
      />
    );
  }

  return (
    <View
      style={{
        width: size,
        height: size,
        borderRadius: radius.full,
        backgroundColor: colors.light.accent,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Text
        style={{
          fontSize: size * 0.35,
          fontWeight: "600",
          color: colors.light.accentForeground,
        }}
      >
        {getInitials(name)}
      </Text>
    </View>
  );
}
