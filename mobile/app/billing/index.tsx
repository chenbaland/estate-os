import { useQuery } from "@tanstack/react-query";
import { ActivityIndicator, ScrollView, Text, View } from "react-native";

import { Badge, Card, CardContent, Header } from "@/components";
import { colors } from "@/constants/theme";
import { api } from "@/lib/api";
import type { BillingInvoice } from "@/types";

function formatAmount(amount: number, currency: string) {
  return new Intl.NumberFormat("en-NG", {
    style: "currency",
    currency: currency || "NGN",
  }).format(amount);
}

export default function BillingScreen() {
  const { data: invoices, isLoading } = useQuery<BillingInvoice[]>({
    queryKey: ["billing"],
    queryFn: async () => {
      const res = await api.getBillingInvoices();
      return res.results ?? [];
    },
  });

  const totalDue =
    invoices
      ?.filter((i: BillingInvoice) => i.status !== "paid")
      .reduce((sum: number, i: BillingInvoice) => sum + i.amount, 0) ?? 0;

  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header title="Billing" subtitle="Invoices and payments" showBack />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 16 }}>
        <Card>
          <CardContent>
            <Text style={{ fontSize: 13, color: colors.light.mutedForeground }}>
              Total outstanding
            </Text>
            <Text
              style={{
                fontSize: 28,
                fontWeight: "700",
                color: colors.light.foreground,
                marginTop: 4,
              }}
            >
              {formatAmount(totalDue, "NGN")}
            </Text>
          </CardContent>
        </Card>

        {isLoading ? (
          <ActivityIndicator color={colors.light.primary} style={{ marginTop: 24 }} />
        ) : invoices && invoices.length > 0 ? (
          invoices.map((invoice: BillingInvoice) => (
            <Card key={invoice.id}>
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
                      {invoice.title}
                    </Text>
                    <Text style={{ color: colors.light.mutedForeground, fontSize: 13 }}>
                      Due {new Date(invoice.due_date).toLocaleDateString()}
                    </Text>
                  </View>
                  <View style={{ alignItems: "flex-end", gap: 6 }}>
                    <Text
                      style={{
                        fontSize: 16,
                        fontWeight: "700",
                        color: colors.light.foreground,
                      }}
                    >
                      {formatAmount(invoice.amount, invoice.currency)}
                    </Text>
                    <Badge
                      label={invoice.status}
                      variant={
                        invoice.status === "paid"
                          ? "success"
                          : invoice.status === "overdue"
                            ? "destructive"
                            : "warning"
                      }
                    />
                  </View>
                </View>
              </CardContent>
            </Card>
          ))
        ) : (
          <Text
            style={{
              textAlign: "center",
              color: colors.light.mutedForeground,
              marginTop: 32,
            }}
          >
            No invoices found
          </Text>
        )}
      </ScrollView>
    </View>
  );
}
