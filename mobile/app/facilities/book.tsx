import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ActivityIndicator, Alert, Pressable, ScrollView, Text, View } from "react-native";

import { Button, Card, CardContent, Header, Input } from "@/components";
import { colors, radius } from "@/constants/theme";
import { api } from "@/lib/api";
import type { Facility } from "@/types";

export default function BookFacilityScreen() {
  const [selected, setSelected] = useState<Facility | null>(null);
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");

  const { data: facilities, isLoading } = useQuery({
    queryKey: ["facilities"],
    queryFn: async () => {
      const res = await api.getFacilities();
      return res.results ?? [];
    },
  });

  const bookMutation = useMutation({
    mutationFn: () =>
      api.bookFacility({
        facility_id: selected!.id,
        start_time: startTime,
        end_time: endTime,
      }),
    onSuccess: () => {
      Alert.alert("Booked", "Your facility booking has been confirmed.");
      setSelected(null);
      setStartTime("");
      setEndTime("");
    },
    onError: (err) => {
      Alert.alert(
        "Booking failed",
        err instanceof Error ? err.message : "Could not complete booking.",
      );
    },
  });

  const handleBook = () => {
    if (!selected || !startTime || !endTime) {
      Alert.alert("Missing fields", "Select a facility and enter start/end times.");
      return;
    }
    bookMutation.mutate();
  };

  return (
    <View style={{ flex: 1, backgroundColor: colors.light.muted }}>
      <Header title="Book Facility" showBack />

      <ScrollView contentContainerStyle={{ padding: 16, gap: 16 }}>
        <Text style={{ fontSize: 15, fontWeight: "600", color: colors.light.foreground }}>
          Select a facility
        </Text>

        {isLoading ? (
          <ActivityIndicator color={colors.light.primary} />
        ) : (
          facilities?.map((facility: Facility) => (
            <Pressable key={facility.id} onPress={() => setSelected(facility)}>
              <Card
                style={{
                  borderColor:
                    selected?.id === facility.id
                      ? colors.light.primary
                      : colors.light.border,
                  borderWidth: selected?.id === facility.id ? 2 : 1,
                }}
              >
                <CardContent>
                  <Text
                    style={{
                      fontSize: 16,
                      fontWeight: "600",
                      color: colors.light.foreground,
                    }}
                  >
                    {facility.name}
                  </Text>
                  <Text
                    style={{
                      color: colors.light.mutedForeground,
                      fontSize: 14,
                      marginTop: 4,
                    }}
                  >
                    {facility.description}
                  </Text>
                  <Text
                    style={{
                      color: colors.light.primary,
                      fontSize: 14,
                      marginTop: 8,
                      fontWeight: "500",
                    }}
                  >
                    ₦{facility.hourly_rate.toLocaleString()}/hr · Cap {facility.capacity}
                  </Text>
                </CardContent>
              </Card>
            </Pressable>
          ))
        )}

        {selected ? (
          <View
            style={{
              backgroundColor: colors.light.card,
              borderRadius: radius.lg,
              padding: 16,
              gap: 12,
              borderWidth: 1,
              borderColor: colors.light.border,
            }}
          >
            <Text style={{ fontWeight: "600", color: colors.light.foreground }}>
              Booking details — {selected.name}
            </Text>
            <Input
              label="Start time (ISO)"
              value={startTime}
              onChangeText={setStartTime}
              placeholder="2026-06-11T14:00:00Z"
            />
            <Input
              label="End time (ISO)"
              value={endTime}
              onChangeText={setEndTime}
              placeholder="2026-06-11T16:00:00Z"
            />
            <Button
              title="Confirm booking"
              onPress={handleBook}
              loading={bookMutation.isPending}
            />
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}
