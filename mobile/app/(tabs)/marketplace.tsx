import { ScrollView, Text, View } from "react-native";

import { Badge, Card, CardContent, Header } from "@/components";
import { colors } from "@/constants/theme";

const LISTINGS = [
  {
    id: "1",
    title: "Fresh organic vegetables",
    seller: "Green Valley Farms",
    price: "₦2,500",
    category: "groceries",
  },
  {
    id: "2",
    title: "Home cleaning service",
    seller: "Sparkle Clean Co.",
    price: "₦8,000",
    category: "services",
  },
  {
    id: "3",
    title: "Kids bicycle — lightly used",
    seller: "Amina O.",
    price: "₦15,000",
    category: "marketplace",
  },
];

export default function MarketplaceScreen() {
  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header title="Marketplace" subtitle="Local vendors and residents" />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
        {LISTINGS.map((listing) => (
          <Card key={listing.id}>
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
                    {listing.title}
                  </Text>
                  <Text style={{ color: colors.light.mutedForeground, fontSize: 14 }}>
                    {listing.seller}
                  </Text>
                </View>
                <Text
                  style={{
                    fontSize: 16,
                    fontWeight: "700",
                    color: colors.light.primary,
                  }}
                >
                  {listing.price}
                </Text>
              </View>
              <Badge label={listing.category} variant="outline" />
            </CardContent>
          </Card>
        ))}
      </ScrollView>
    </View>
  );
}
