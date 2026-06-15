import { ScrollView, Text, View } from "react-native";

import { Badge, Card, CardContent, Header } from "@/components";
import { colors, radius } from "@/constants/theme";

const ANNOUNCEMENTS = [
  {
    id: "1",
    title: "Estate AGM — June 28",
    body: "Annual general meeting at the community hall. RSVP by June 20.",
    type: "event" as const,
  },
  {
    id: "2",
    title: "Water maintenance scheduled",
    body: "Water supply interruption on Block C, 9 AM – 12 PM Saturday.",
    type: "notice" as const,
  },
  {
    id: "3",
    title: "Neighborhood watch drive",
    body: "Join the security team for our monthly patrol orientation.",
    type: "community" as const,
  },
];

export default function CommunityScreen() {
  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header title="Community" subtitle="Announcements and events" />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
        {ANNOUNCEMENTS.map((item) => (
          <Card key={item.id}>
            <CardContent style={{ gap: 8 }}>
              <View
                style={{
                  flexDirection: "row",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Text
                  style={{
                    fontSize: 16,
                    fontWeight: "600",
                    color: colors.light.foreground,
                    flex: 1,
                  }}
                >
                  {item.title}
                </Text>
                <Badge
                  label={item.type}
                  variant={item.type === "event" ? "info" : "outline"}
                />
              </View>
              <Text style={{ color: colors.light.mutedForeground, fontSize: 14, lineHeight: 20 }}>
                {item.body}
              </Text>
            </CardContent>
          </Card>
        ))}

        <View
          style={{
            backgroundColor: colors.light.accent,
            borderRadius: radius.lg,
            padding: 16,
            marginTop: 8,
          }}
        >
          <Text style={{ fontWeight: "600", color: colors.light.accentForeground }}>
            Community forums coming soon
          </Text>
          <Text
            style={{
              color: colors.light.accentForeground,
              fontSize: 14,
              marginTop: 4,
              opacity: 0.8,
            }}
          >
            Discuss topics, vote on proposals, and connect with neighbors.
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}
