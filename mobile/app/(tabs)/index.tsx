import { Ionicons } from "@expo/vector-icons";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "expo-router";
import { Pressable, ScrollView, Text, View } from "react-native";

import { Avatar, Badge, Card, CardContent, Header } from "@/components";
import { colors, radius } from "@/constants/theme";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { useEstateStore } from "@/stores/estate";
import type { VisitorPass } from "@/types";

const QUICK_ACTIONS = [
  { label: "Visitor Pass", icon: "people" as const, href: "/visitors/create" },
  { label: "SOS", icon: "warning" as const, href: "/sos", color: colors.light.destructive },
  { label: "Billing", icon: "card" as const, href: "/billing" },
  { label: "Book Facility", icon: "calendar" as const, href: "/facilities/book" },
  { label: "Maintenance", icon: "construct" as const, href: "/maintenance/create" },
  { label: "AI Concierge", icon: "sparkles" as const, href: "/ai/chat" },
];

export default function HomeScreen() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { currentEstate } = useEstateStore();

  const { data: visitors } = useQuery<VisitorPass[]>({
    queryKey: ["visitors"],
    queryFn: async () => {
      const res = await api.getVisitors();
      return res.results ?? [];
    },
  });

  const activeVisitors =
    visitors?.filter((v: VisitorPass) => v.status === "active").length ?? 0;

  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header
        title={currentEstate?.name ?? "EstateOS"}
        subtitle={`Welcome, ${user?.first_name ?? "Resident"}`}
        rightAction={
          <Avatar
            src={user?.avatar}
            name={`${user?.first_name ?? ""} ${user?.last_name ?? ""}`}
            size={36}
          />
        }
      />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 16 }}>
        <View style={{ flexDirection: "row", gap: 12 }}>
          <Card style={{ flex: 1 }}>
            <CardContent>
              <Text style={{ fontSize: 13, color: colors.light.mutedForeground }}>
                Active Visitors
              </Text>
              <Text
                style={{
                  fontSize: 28,
                  fontWeight: "700",
                  color: colors.light.foreground,
                  marginTop: 4,
                }}
              >
                {activeVisitors}
              </Text>
            </CardContent>
          </Card>
          <Card style={{ flex: 1 }}>
            <CardContent>
              <Text style={{ fontSize: 13, color: colors.light.mutedForeground }}>
                Estate
              </Text>
              <Text
                style={{
                  fontSize: 16,
                  fontWeight: "600",
                  color: colors.light.foreground,
                  marginTop: 8,
                }}
                numberOfLines={2}
              >
                {currentEstate?.city ?? "Select estate"}
              </Text>
            </CardContent>
          </Card>
        </View>

        <Text
          style={{
            fontSize: 16,
            fontWeight: "600",
            color: colors.light.foreground,
          }}
        >
          Quick Actions
        </Text>

        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>
          {QUICK_ACTIONS.map((action) => (
            <Pressable
              key={action.label}
              onPress={() => router.push(action.href as never)}
              style={{
                width: "30%",
                minWidth: 100,
                backgroundColor: colors.light.card,
                borderRadius: radius.lg,
                borderWidth: 1,
                borderColor: colors.light.border,
                padding: 16,
                alignItems: "center",
                gap: 8,
              }}
            >
              <Ionicons
                name={action.icon}
                size={24}
                color={action.color ?? colors.light.primary}
              />
              <Text
                style={{
                  fontSize: 12,
                  fontWeight: "500",
                  color: colors.light.foreground,
                  textAlign: "center",
                }}
              >
                {action.label}
              </Text>
            </Pressable>
          ))}
        </View>

        <Card>
          <CardContent>
            <View
              style={{
                flexDirection: "row",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 12,
              }}
            >
              <Text
                style={{
                  fontSize: 16,
                  fontWeight: "600",
                  color: colors.light.foreground,
                }}
              >
                Recent Visitors
              </Text>
              <Badge label="Today" variant="outline" />
            </View>
            {visitors && visitors.length > 0 ? (
              visitors.slice(0, 3).map((visitor: VisitorPass) => (
                <View
                  key={visitor.id}
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    alignItems: "center",
                    paddingVertical: 10,
                    borderTopWidth: 1,
                    borderTopColor: colors.light.border,
                  }}
                >
                  <Text style={{ color: colors.light.foreground, fontWeight: "500" }}>
                    {visitor.visitor_name}
                  </Text>
                  <Badge
                    label={visitor.status}
                    variant={visitor.status === "active" ? "success" : "outline"}
                  />
                </View>
              ))
            ) : (
              <Text style={{ color: colors.light.mutedForeground, fontSize: 14 }}>
                No visitors yet. Create a pass to get started.
              </Text>
            )}
          </CardContent>
        </Card>
      </ScrollView>
    </View>
  );
}
