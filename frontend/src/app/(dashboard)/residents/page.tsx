"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ModulePage } from "@/components/shared/ModulePage";
import { toast } from "@/components/ui/toast";
import { useAuth } from "@/hooks/useAuth";
import { hasRole } from "@/lib/auth";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";
import { api } from "@/lib/api";
import type { ResidentProfile, ResidentType, Unit } from "@/types";

export default function ResidentsPage() {
  const { roles } = useAuth();
  const queryClient = useQueryClient();
  const isAdmin = hasRole(roles, ["super_admin", "estate_admin", "finance_admin"]);
  const [selectedUnits, setSelectedUnits] = useState<Record<string, string>>({});
  const [selectedTypes, setSelectedTypes] = useState<Record<string, ResidentType>>({});

  const { data: pendingProfiles = [], isLoading } = useQuery({
    queryKey: ["pending-residents"],
    queryFn: async () => {
      const response = await api.getResidentProfiles({ status: "pending" });
      return response.results;
    },
    enabled: isAdmin,
  });

  const { data: units = [] } = useQuery({
    queryKey: ["estate-units"],
    queryFn: async () => {
      const response = await api.getUnits();
      return response.results;
    },
    enabled: isAdmin && pendingProfiles.length > 0,
  });

  const activateMutation = useMutation({
    mutationFn: ({
      profileId,
      unitId,
      residentType,
    }: {
      profileId: string;
      unitId: string;
      residentType: ResidentType;
    }) => api.activateResidentProfile(profileId, unitId, residentType),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pending-residents"] });
      toast.success("Resident profile activated.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const rejectMutation = useMutation({
    mutationFn: (profileId: string) => api.rejectResidentProfile(profileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pending-residents"] });
      toast.success("Registration request declined.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <ModulePage
      title="Residents"
      description={MODULE_DESCRIPTIONS.residents}
      iconKey="residents"
      badge={isAdmin && pendingProfiles.length > 0 ? `${pendingProfiles.length} pending` : "Active"}
    >
      {isAdmin ? (
        <Card>
          <CardHeader>
            <CardTitle>Pending registrations</CardTitle>
            <CardDescription>
              Review new sign-ups, confirm the unit, set homeowner or tenant, then activate access.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading pending registrations...</p>
            ) : pendingProfiles.length === 0 ? (
              <p className="text-sm text-muted-foreground">No pending resident registrations.</p>
            ) : (
              pendingProfiles.map((profile) => (
                <PendingResidentRow
                  key={profile.id}
                  profile={profile}
                  units={units}
                  selectedUnitId={selectedUnits[profile.id] ?? profile.unit ?? ""}
                  selectedType={selectedTypes[profile.id] ?? ""}
                  onUnitChange={(unitId) =>
                    setSelectedUnits((current) => ({ ...current, [profile.id]: unitId }))
                  }
                  onTypeChange={(residentType) =>
                    setSelectedTypes((current) => ({ ...current, [profile.id]: residentType }))
                  }
                  onActivate={() => {
                    const unitId = selectedUnits[profile.id] || profile.unit || "";
                    const residentType = selectedTypes[profile.id];
                    if (!unitId) {
                      toast.error("Select a unit before activating.");
                      return;
                    }
                    if (!residentType) {
                      toast.error("Select homeowner or tenant before activating.");
                      return;
                    }
                    activateMutation.mutate({ profileId: profile.id, unitId, residentType });
                  }}
                  onReject={() => rejectMutation.mutate(profile.id)}
                  isActivating={activateMutation.isPending}
                  isRejecting={rejectMutation.isPending}
                />
              ))
            )}
          </CardContent>
        </Card>
      ) : (
        <p className="text-sm text-muted-foreground">
          Resident directory and onboarding tools are available to estate administrators.
        </p>
      )}
    </ModulePage>
  );
}

function PendingResidentRow({
  profile,
  units,
  selectedUnitId,
  selectedType,
  onUnitChange,
  onTypeChange,
  onActivate,
  onReject,
  isActivating,
  isRejecting,
}: {
  profile: ResidentProfile;
  units: Unit[];
  selectedUnitId: string;
  selectedType: ResidentType | "";
  onUnitChange: (unitId: string) => void;
  onTypeChange: (residentType: ResidentType) => void;
  onActivate: () => void;
  onReject: () => void;
  isActivating: boolean;
  isRejecting: boolean;
}) {
  const name = [profile.user_first_name, profile.user_last_name].filter(Boolean).join(" ");

  return (
    <div className="rounded-lg border p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="font-medium">{name || profile.user_email}</p>
          <p className="text-sm text-muted-foreground">{profile.user_email}</p>
          {profile.unit_number ? (
            <p className="mt-1 text-sm">Registered for unit {profile.unit_number}</p>
          ) : null}
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <Select value={selectedUnitId} onValueChange={onUnitChange}>
            <SelectTrigger className="w-full sm:w-[160px]">
              <SelectValue placeholder="Unit" />
            </SelectTrigger>
            <SelectContent>
              {units.map((unit) => (
                <SelectItem key={unit.id} value={unit.id}>
                  {unit.unit_number}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={selectedType}
            onValueChange={(value) => onTypeChange(value as ResidentType)}
          >
            <SelectTrigger className="w-full sm:w-[160px]">
              <SelectValue placeholder="Resident type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="owner">Homeowner</SelectItem>
              <SelectItem value="tenant">Tenant</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={onActivate} disabled={isActivating || isRejecting}>
            Activate
          </Button>
          <Button variant="outline" onClick={onReject} disabled={isActivating || isRejecting}>
            Decline
          </Button>
        </div>
      </div>
    </div>
  );
}
