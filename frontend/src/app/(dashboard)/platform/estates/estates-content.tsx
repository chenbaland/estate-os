"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "@/components/ui/toast";
import { api } from "@/lib/api";
import type {
  CreatePlatformEstatePayload,
  PlatformEstate,
  UpdatePlatformEstatePayload,
} from "@/types";

const EMPTY_FORM: CreatePlatformEstatePayload = {
  name: "",
  address_line1: "",
  city: "",
  state: "",
  country: "NG",
  contact_email: "",
  contact_phone: "",
  total_units: 0,
  estate_type: "gated",
  tier: "standard",
  timezone: "Africa/Lagos",
  currency: "NGN",
};

function estateToForm(estate: PlatformEstate): UpdatePlatformEstatePayload {
  return {
    name: estate.name,
    address_line1: estate.address_line1,
    city: estate.city,
    state: estate.state,
    country: estate.country,
    contact_email: estate.contact_email,
    contact_phone: estate.contact_phone,
    total_units: estate.total_units,
    estate_type: estate.estate_type,
    tier: estate.tier,
    timezone: estate.timezone,
    currency: estate.currency,
    description: estate.description,
  };
}

export default function PlatformEstatesContent() {
  const queryClient = useQueryClient();
  const searchParams = useSearchParams();
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [editingEstate, setEditingEstate] = useState<PlatformEstate | null>(null);
  const [createForm, setCreateForm] = useState<CreatePlatformEstatePayload>(EMPTY_FORM);
  const [editForm, setEditForm] = useState<UpdatePlatformEstatePayload>(EMPTY_FORM);

  useEffect(() => {
    if (searchParams.get("create") === "true") {
      setCreateOpen(true);
    }
  }, [searchParams]);

  const { data: estates = [], isLoading } = useQuery({
    queryKey: ["platform-estates"],
    queryFn: async () => {
      const response = await api.getPlatformEstates();
      return response.results;
    },
  });

  const invalidateEstates = () => {
    queryClient.invalidateQueries({ queryKey: ["platform-estates"] });
    queryClient.invalidateQueries({ queryKey: ["platform-overview"] });
    queryClient.invalidateQueries({ queryKey: ["public-estates"] });
    queryClient.invalidateQueries({ queryKey: ["platform-audit-logs"] });
  };

  const createMutation = useMutation({
    mutationFn: (payload: CreatePlatformEstatePayload) => api.createPlatformEstate(payload),
    onSuccess: () => {
      invalidateEstates();
      setCreateForm(EMPTY_FORM);
      setCreateOpen(false);
      toast.success("Estate created successfully.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdatePlatformEstatePayload }) =>
      api.updatePlatformEstate(id, payload),
    onSuccess: () => {
      invalidateEstates();
      setEditOpen(false);
      setEditingEstate(null);
      toast.success("Estate updated successfully.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const deactivateMutation = useMutation({
    mutationFn: (estateId: string) => api.deactivatePlatformEstate(estateId),
    onSuccess: () => {
      invalidateEstates();
      toast.success("Estate deactivated.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const activateMutation = useMutation({
    mutationFn: (estateId: string) => api.activatePlatformEstate(estateId),
    onSuccess: () => {
      invalidateEstates();
      toast.success("Estate activated.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  function updateCreateField<K extends keyof CreatePlatformEstatePayload>(
    key: K,
    value: CreatePlatformEstatePayload[K],
  ) {
    setCreateForm((current) => ({ ...current, [key]: value }));
  }

  function updateEditField<K extends keyof UpdatePlatformEstatePayload>(
    key: K,
    value: UpdatePlatformEstatePayload[K],
  ) {
    setEditForm((current) => ({ ...current, [key]: value }));
  }

  function openEditDialog(estate: PlatformEstate) {
    setEditingEstate(estate);
    setEditForm(estateToForm(estate));
    setEditOpen(true);
  }

  const isMutating =
    createMutation.isPending ||
    updateMutation.isPending ||
    deactivateMutation.isPending ||
    activateMutation.isPending;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-muted-foreground">
          Create and manage estates on the platform. New estates receive default roles automatically.
        </p>
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogTrigger asChild>
            <Button>Create estate</Button>
          </DialogTrigger>
          <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Create estate</DialogTitle>
              <DialogDescription>
                Provision a new estate tenant with default admin and resident roles.
              </DialogDescription>
            </DialogHeader>
            <EstateFormFields
              form={createForm}
              onFieldChange={updateCreateField}
              idPrefix="create"
            />
            <DialogFooter>
              <Button
                onClick={() => createMutation.mutate(createForm)}
                disabled={
                  createMutation.isPending ||
                  !createForm.name ||
                  !createForm.address_line1 ||
                  !createForm.city ||
                  !createForm.state
                }
              >
                {createMutation.isPending ? "Creating..." : "Create estate"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit estate</DialogTitle>
            <DialogDescription>
              Update estate details for {editingEstate?.name ?? "this estate"}.
            </DialogDescription>
          </DialogHeader>
          <EstateFormFields form={editForm} onFieldChange={updateEditField} idPrefix="edit" />
          <DialogFooter>
            <Button
              onClick={() =>
                editingEstate &&
                updateMutation.mutate({ id: editingEstate.id, payload: editForm })
              }
              disabled={
                updateMutation.isPending ||
                !editForm.name ||
                !editForm.address_line1 ||
                !editForm.city ||
                !editForm.state
              }
            >
              {updateMutation.isPending ? "Saving..." : "Save changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Card>
        <CardHeader>
          <CardTitle>All estates</CardTitle>
          <CardDescription>Platform-wide estate tenants and onboarding status</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading estates...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Estate</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Units</TableHead>
                  <TableHead>Admins</TableHead>
                  <TableHead>Pending</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {estates.map((estate) => (
                  <TableRow key={estate.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{estate.name}</p>
                        <p className="text-xs text-muted-foreground">{estate.slug}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      {estate.city}, {estate.state}
                    </TableCell>
                    <TableCell>{estate.total_units}</TableCell>
                    <TableCell>{estate.admin_count}</TableCell>
                    <TableCell>{estate.pending_residents}</TableCell>
                    <TableCell>
                      <Badge variant={estate.is_active ? "default" : "secondary"}>
                        {estate.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openEditDialog(estate)}
                          disabled={isMutating}
                        >
                          Edit
                        </Button>
                        {estate.is_active ? (
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => deactivateMutation.mutate(estate.id)}
                            disabled={isMutating}
                          >
                            Deactivate
                          </Button>
                        ) : (
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => activateMutation.mutate(estate.id)}
                            disabled={isMutating}
                          >
                            Activate
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function EstateFormFields<T extends CreatePlatformEstatePayload>({
  form,
  onFieldChange,
  idPrefix,
}: {
  form: T;
  onFieldChange: <K extends keyof T>(key: K, value: T[K]) => void;
  idPrefix: string;
}) {
  return (
    <div className="grid gap-4 py-2">
      <div className="grid gap-2">
        <Label htmlFor={`${idPrefix}-name`}>Estate name</Label>
        <Input
          id={`${idPrefix}-name`}
          value={form.name}
          onChange={(e) => onFieldChange("name", e.target.value)}
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor={`${idPrefix}-address`}>Address</Label>
        <Input
          id={`${idPrefix}-address`}
          value={form.address_line1}
          onChange={(e) => onFieldChange("address_line1", e.target.value)}
        />
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-2">
          <Label htmlFor={`${idPrefix}-city`}>City</Label>
          <Input
            id={`${idPrefix}-city`}
            value={form.city}
            onChange={(e) => onFieldChange("city", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${idPrefix}-state`}>State</Label>
          <Input
            id={`${idPrefix}-state`}
            value={form.state}
            onChange={(e) => onFieldChange("state", e.target.value)}
          />
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-2">
          <Label>Estate type</Label>
          <Select
            value={form.estate_type}
            onValueChange={(value) => onFieldChange("estate_type", value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="gated">Gated community</SelectItem>
              <SelectItem value="apartment">Apartment complex</SelectItem>
              <SelectItem value="townhouse">Townhouse estate</SelectItem>
              <SelectItem value="mixed_use">Mixed use</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-2">
          <Label>Tier</Label>
          <Select value={form.tier} onValueChange={(value) => onFieldChange("tier", value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="standard">Standard</SelectItem>
              <SelectItem value="premium">Premium</SelectItem>
              <SelectItem value="enterprise">Enterprise</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-2">
          <Label htmlFor={`${idPrefix}-contact_email`}>Contact email</Label>
          <Input
            id={`${idPrefix}-contact_email`}
            type="email"
            value={form.contact_email ?? ""}
            onChange={(e) => onFieldChange("contact_email", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor={`${idPrefix}-total_units`}>Total units</Label>
          <Input
            id={`${idPrefix}-total_units`}
            type="number"
            min={0}
            value={form.total_units ?? 0}
            onChange={(e) => onFieldChange("total_units", Number(e.target.value))}
          />
        </div>
      </div>
    </div>
  );
}
