import { Ionicons } from "@expo/vector-icons";
import type { BottomTabBarProps } from "@react-navigation/bottom-tabs";
import { Pressable, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { colors, layout } from "@/constants/theme";

const TAB_ICONS: Record<string, keyof typeof Ionicons.glyphMap> = {
  index: "home",
  visitors: "people",
  community: "chatbubbles",
  marketplace: "storefront",
  profile: "person",
};

const TAB_LABELS: Record<string, string> = {
  index: "Home",
  visitors: "Visitors",
  community: "Community",
  marketplace: "Market",
  profile: "Profile",
};

export function TabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();

  return (
    <View
      style={{
        flexDirection: "row",
        backgroundColor: colors.light.background,
        borderTopWidth: 1,
        borderTopColor: colors.light.border,
        paddingBottom: insets.bottom,
        height: layout.tabBarHeight + insets.bottom,
      }}
    >
      {state.routes.map((route, index) => {
        const { options } = descriptors[route.key];
        const isFocused = state.index === index;
        const iconName = TAB_ICONS[route.name] ?? "ellipse";
        const label = TAB_LABELS[route.name] ?? options.title ?? route.name;

        const onPress = () => {
          const event = navigation.emit({
            type: "tabPress",
            target: route.key,
            canPreventDefault: true,
          });

          if (!isFocused && !event.defaultPrevented) {
            navigation.navigate(route.name, route.params);
          }
        };

        return (
          <Pressable
            key={route.key}
            onPress={onPress}
            style={{
              flex: 1,
              alignItems: "center",
              justifyContent: "center",
              paddingTop: 8,
              gap: 4,
            }}
          >
            <Ionicons
              name={iconName}
              size={22}
              color={isFocused ? colors.light.primary : colors.light.mutedForeground}
            />
            <Text
              style={{
                fontSize: 11,
                fontWeight: isFocused ? "600" : "400",
                color: isFocused
                  ? colors.light.primary
                  : colors.light.mutedForeground,
              }}
            >
              {label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}
