/**
 * Design tokens aligned with frontend/src/styles/tokens.css
 * HSL values converted to hex for React Native StyleSheet usage.
 */

export const colors = {
  light: {
    background: "#FFFFFF",
    foreground: "#09090B",
    card: "#FFFFFF",
    cardForeground: "#09090B",
    primary: "#7C3AED",
    primaryForeground: "#FAFAFA",
    secondary: "#F4F4F5",
    secondaryForeground: "#18181B",
    muted: "#F4F4F5",
    mutedForeground: "#71717A",
    accent: "#EDE9FE",
    accentForeground: "#5B21B6",
    destructive: "#EF4444",
    destructiveForeground: "#FAFAFA",
    border: "#E4E4E7",
    input: "#E4E4E7",
    ring: "#7C3AED",
    success: "#16A34A",
    warning: "#F59E0B",
    info: "#0EA5E9",
    brandGradientFrom: "#7C3AED",
    brandGradientTo: "#2563EB",
  },
  dark: {
    background: "#09090B",
    foreground: "#FAFAFA",
    card: "#18181B",
    cardForeground: "#FAFAFA",
    primary: "#8B5CF6",
    primaryForeground: "#FAFAFA",
    secondary: "#27272A",
    secondaryForeground: "#FAFAFA",
    muted: "#27272A",
    mutedForeground: "#A1A1AA",
    accent: "#2E1065",
    accentForeground: "#C4B5FD",
    destructive: "#7F1D1D",
    destructiveForeground: "#FAFAFA",
    border: "#27272A",
    input: "#27272A",
    ring: "#8B5CF6",
    success: "#16A34A",
    warning: "#F59E0B",
    info: "#0EA5E9",
    brandGradientFrom: "#8B5CF6",
    brandGradientTo: "#3B82F6",
  },
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  "2xl": 32,
  "3xl": 48,
} as const;

export const radius = {
  sm: 8,
  md: 10,
  lg: 12,
  xl: 16,
  full: 9999,
} as const;

export const fontSize = {
  xs: 12,
  sm: 14,
  base: 16,
  lg: 18,
  xl: 20,
  "2xl": 24,
  "3xl": 30,
} as const;

export const fontWeight = {
  normal: "400" as const,
  medium: "500" as const,
  semibold: "600" as const,
  bold: "700" as const,
};

export const shadows = {
  sm: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  lg: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 15,
    elevation: 6,
  },
} as const;

export const layout = {
  headerHeight: 56,
  tabBarHeight: 64,
  contentMaxWidth: 1400,
} as const;

export type ColorScheme = keyof typeof colors;
export type ThemeColors = (typeof colors)["light"];
