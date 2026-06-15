import { useQuery } from "@tanstack/react-query";
import { useRouter } from "expo-router";
import { ActivityIndicator, Pressable, ScrollView, Text, View } from "react-native";

import { Badge, Button, Card, CardContent, Header } from "@/components";
import { colors } from "@/constants/theme";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type { VisitorPass } from "@/types";

export default function VisitorsScreen() {
  const router = useRouter();
  const { roles } = useAuthStore();
  const isSecurity = roles.some((r) =>
    ["security_admin", "security_personnel"].includes(r.code),
  );

  const { data: visitors, isLoading, refetch, isRefetching } = useQuery<VisitorPass[]>({
    queryKey: ["visitors"],
    queryFn: async () => {
      const res = await api.getVisitors();
      return res.results ?? [];
    },
  });

  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header
        title="Visitors"
        subtitle="Manage guest access passes"
        rightAction={
          <View style={{ flexDirection: "row", gap: 8 }}>
            {isSecurity ? (
              <Button
                title="Scan"
                size="sm"
                variant="outline"
                onPress={() => router.push("/visitors/scan")}
              />
            ) : null}
            <Button
              title="New Pass"
              size="sm"
              onPress={() => router.push("/visitors/create")}
            />
          </View>
        }
      />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
        {isLoading ? (
          <ActivityIndicator color={colors.light.primary} style={{ marginTop: 32 }} />
        ) : visitors && visitors.length > 0 ? (
          visitors.map((visitor: VisitorPass) => (
            <Card key={visitor.id}>
              <CardContent>
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  }}
                >
                  <View style={{ flex: 1, gap: 4 }}>
                    <Text
                      style={{
                        fontSize: 16,
                        fontWeight: "600",
                        color: colors.light.foreground,
                      }}
                    >
                      {visitor.visitor_name}
                    </Text>
                    <Text style={{ color: colors.light.mutedForeground, fontSize: 14 }}>
                      {visitor.purpose}
                    </Text>
                    <Text style={{ color: colors.light.mutedForeground, fontSize: 12 }}>
                      Valid until {new Date(visitor.valid_until).toLocaleString()}
                    </Text>
                  </View>
                  <Badge
                    label={visitor.status}
                    variant={
                      visitor.status === "active"
                        ? "success"
                        : visitor.status === "expired"
                          ? "warning"
                          : "outline"
                    }
                  />
                </View>
              </CardContent>
            </Card>
          ))
        ) : (
          <View style={{ alignItems: "center", paddingTop: 48, gap: 16 }}>
            <Text style={{ color: colors.light.mutedForeground, fontSize: 16 }}>
              No visitor passes yet
            </Text>
            <Button
              title="Create visitor pass"
              onPress={() => router.push("/visitors/create")}
            />
          </View>
        )}

        <Pressable onPress={() => refetch()} style={{ alignItems: "center", padding: 16 }}>
          <Text style={{ color: colors.light.primary }}>
            {isRefetching ? "Refreshing..." : "Pull to refresh"}
          </Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}
