"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

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
import type { AssignPlatformAdminPayload } from "@/types";

const EMPTY_FORM: AssignPlatformAdminPayload = {
  email: "",
  first_name: "",
  last_name: "",
  estate_id: "",
  role_code: "estate_admin",
};

export default function PlatformAdminsPage() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<AssignPlatformAdminPayload>(EMPTY_FORM);

  const { data: admins = [], isLoading } = useQuery({
    queryKey: ["platform-admins"],
    queryFn: async () => {
      const response = await api.getPlatformAdmins();
      return response.results;
    },
  });

  const { data: estates = [] } = useQuery({
    queryKey: ["platform-estates"],
    queryFn: async () => {
      const response = await api.getPlatformEstates();
      return response.results;
    },
  });

  const assignMutation = useMutation({
    mutationFn: (payload: AssignPlatformAdminPayload) => api.assignPlatformAdmin(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["platform-admins"] });
      queryClient.invalidateQueries({ queryKey: ["platform-overview"] });
      setForm(EMPTY_FORM);
      setOpen(false);
      toast.success("Administrator assigned. An invite email was sent.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const revokeMutation = useMutation({
    mutationFn: (assignmentId: string) => api.revokePlatformAdmin(assignmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["platform-admins"] });
      queryClient.invalidateQueries({ queryKey: ["platform-overview"] });
      toast.success("Administrator access revoked.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-muted-foreground">
          Assign estate administrators and operational admins to manage each tenant estate.
        </p>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>Assign admin</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Assign estate admin</DialogTitle>
              <DialogDescription>
                Existing users are linked by email. New users receive a generated password and staff access.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-2">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm((current) => ({ ...current, email: e.target.value }))}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="grid gap-2">
                  <Label htmlFor="first_name">First name</Label>
                  <Input
                    id="first_name"
                    value={form.first_name}
                    onChange={(e) =>
                      setForm((current) => ({ ...current, first_name: e.target.value }))
                    }
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="last_name">Last name</Label>
                  <Input
                    id="last_name"
                    value={form.last_name}
                    onChange={(e) =>
                      setForm((current) => ({ ...current, last_name: e.target.value }))
                    }
                  />
                </div>
              </div>
              <div className="grid gap-2">
                <Label>Estate</Label>
                <Select
                  value={form.estate_id}
                  onValueChange={(value) =>
                    setForm((current) => ({ ...current, estate_id: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select estate" />
                  </SelectTrigger>
                  <SelectContent>
                    {estates.map((estate) => (
                      <SelectItem key={estate.id} value={estate.id}>
                        {estate.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label>Admin role</Label>
                <Select
                  value={form.role_code}
                  onValueChange={(value) =>
                    setForm((current) => ({
                      ...current,
                      role_code: value as AssignPlatformAdminPayload["role_code"],
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="estate_admin">Estate Admin</SelectItem>
                    <SelectItem value="finance_admin">Finance Admin</SelectItem>
                    <SelectItem value="security_admin">Security Admin</SelectItem>
                    <SelectItem value="facility_admin">Facility Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button
                onClick={() => assignMutation.mutate(form)}
                disabled={assignMutation.isPending || !form.email || !form.estate_id}
              >
                {assignMutation.isPending ? "Assigning..." : "Assign admin"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Estate administrators</CardTitle>
          <CardDescription>Active admin assignments across all estates</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading administrators...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Admin</TableHead>
                  <TableHead>Estate</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {admins.map((admin) => (
                  <TableRow key={admin.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">
                          {[admin.user_first_name, admin.user_last_name]
                            .filter(Boolean)
                            .join(" ") || admin.user_email}
                        </p>
                        <p className="text-xs text-muted-foreground">{admin.user_email}</p>
                      </div>
                    </TableCell>
                    <TableCell>{admin.estate_name}</TableCell>
                    <TableCell>{admin.role_name}</TableCell>
                    <TableCell>
                      <Badge variant={admin.is_active ? "default" : "secondary"}>
                        {admin.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={revokeMutation.isPending}
                        onClick={() => revokeMutation.mutate(admin.id)}
                      >
                        Revoke
                      </Button>
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
