"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { ModulePage } from "@/components/shared/ModulePage";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/toast";
import { useAuth } from "@/hooks/useAuth";
import { useEstate } from "@/hooks/useEstate";
import { hasRole } from "@/lib/auth";
import { api, getEstateId } from "@/lib/api";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";
import { formatRelativeTime } from "@/lib/utils";
import type { BlacklistEntry, VisitorLog, VisitorPass } from "@/types";

export default function VisitorsPage() {
  const { roles, memberships } = useAuth();
  const { currentEstate, isLoading: estateLoading } = useEstate();
  const estateId = currentEstate?.id ?? getEstateId();
  const isStaffView = hasRole(roles, [
    "super_admin",
    "estate_admin",
    "security_admin",
    "security_personnel",
  ]);
  const residentProfileId = memberships.find(
    (m) => m.estate_id === estateId && m.status === "active",
  )?.resident_profile_id;
  const canCreatePass = Boolean(residentProfileId);

  const { data: passes = [], isLoading: passesLoading } = useQuery({
    queryKey: ["visitor-passes", estateId, residentProfileId, isStaffView],
    queryFn: async () => {
      const params =
        isStaffView || !residentProfileId ? undefined : { host: residentProfileId };
      const response = await api.getVisitorPasses(params);
      return response.results;
    },
    enabled: Boolean(estateId) && (isStaffView || Boolean(residentProfileId)),
  });

  const { data: logs = [], isLoading: logsLoading } = useQuery({
    queryKey: ["visitor-logs", estateId],
    queryFn: async () => {
      const response = await api.getVisitorLogs();
      return response.results;
    },
    enabled: Boolean(estateId) && isStaffView,
  });

  const { data: blacklist = [], isLoading: blacklistLoading } = useQuery({
    queryKey: ["visitor-blacklist", estateId],
    queryFn: async () => {
      const response = await api.getBlacklist({ is_active: "true" });
      return response.results;
    },
    enabled: Boolean(estateId) && isStaffView,
  });

  const activePasses = passes.filter((p) => p.status === "active").length;
  const badge = activePasses > 0 ? `${activePasses} active` : "Live";

  if (estateLoading || !estateId) {
    return (
      <ModulePage
        title="Visitors"
        description={MODULE_DESCRIPTIONS.visitors}
        iconKey="visitors"
        badge="Loading"
      >
        <p className="text-sm text-muted-foreground">Loading estate context…</p>
      </ModulePage>
    );
  }

  if (!isStaffView && !residentProfileId) {
    return (
      <ModulePage
        title="Visitors"
        description={MODULE_DESCRIPTIONS.visitors}
        iconKey="visitors"
        badge="Active"
      >
        <p className="text-sm text-muted-foreground">
          Visitor passes are available to active residents and security staff.
        </p>
      </ModulePage>
    );
  }

  return (
    <ModulePage
      title="Visitors"
      description={MODULE_DESCRIPTIONS.visitors}
      iconKey="visitors"
      badge={badge}
    >
      <Tabs defaultValue="passes" className="space-y-4">
        <TabsList>
          <TabsTrigger value="passes">Passes</TabsTrigger>
          {isStaffView ? (
            <>
              <TabsTrigger value="logs">Gate logs</TabsTrigger>
              <TabsTrigger value="blacklist">Blacklist</TabsTrigger>
            </>
          ) : null}
        </TabsList>

        <TabsContent value="passes" className="space-y-4">
          {canCreatePass ? (
            <CreatePassForm hostId={residentProfileId!} estateId={estateId} />
          ) : null}
          <PassesTable
            passes={passes}
            isLoading={passesLoading}
            canRevoke={canCreatePass || isStaffView}
            estateId={estateId}
          />
        </TabsContent>

        {isStaffView ? (
          <>
            <TabsContent value="logs">
              <LogsTable logs={logs} isLoading={logsLoading} />
            </TabsContent>
            <TabsContent value="blacklist">
              <BlacklistTable entries={blacklist} isLoading={blacklistLoading} />
            </TabsContent>
          </>
        ) : null}
      </Tabs>
    </ModulePage>
  );
}

function CreatePassForm({ hostId, estateId }: { hostId: string; estateId: string }) {
  const queryClient = useQueryClient();
  const [visitorName, setVisitorName] = useState("");
  const [visitorPhone, setVisitorPhone] = useState("");
  const [purpose, setPurpose] = useState("");

  const createMutation = useMutation({
    mutationFn: () => {
      const validUntil = new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString();
      return api.createVisitorPass({
        host: hostId,
        visitor_name: visitorName.trim(),
        visitor_phone: visitorPhone.trim() || undefined,
        purpose: purpose.trim() || undefined,
        pass_type: "single",
        valid_until: validUntil,
        max_entries: 1,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["visitor-passes", estateId] });
      setVisitorName("");
      setVisitorPhone("");
      setPurpose("");
      toast.success("Visitor pass created.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Issue visitor pass</CardTitle>
        <CardDescription>
          Pre-authorize a guest. A QR code is generated automatically for gate entry.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
          onSubmit={(event) => {
            event.preventDefault();
            if (!visitorName.trim()) {
              toast.error("Visitor name is required.");
              return;
            }
            createMutation.mutate();
          }}
        >
          <div className="space-y-2">
            <Label htmlFor="visitor-name">Visitor name</Label>
            <Input
              id="visitor-name"
              value={visitorName}
              onChange={(e) => setVisitorName(e.target.value)}
              placeholder="Full name"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="visitor-phone">Phone</Label>
            <Input
              id="visitor-phone"
              value={visitorPhone}
              onChange={(e) => setVisitorPhone(e.target.value)}
              placeholder="+234…"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="visitor-purpose">Purpose</Label>
            <Input
              id="visitor-purpose"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              placeholder="Delivery, visit, etc."
            />
          </div>
          <div className="flex items-end">
            <Button type="submit" disabled={createMutation.isPending} className="w-full">
              Create pass
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

function PassesTable({
  passes,
  isLoading,
  canRevoke,
  estateId,
}: {
  passes: VisitorPass[];
  isLoading: boolean;
  canRevoke: boolean;
  estateId: string;
}) {
  const queryClient = useQueryClient();

  const revokeMutation = useMutation({
    mutationFn: (passId: string) => api.revokeVisitorPass(passId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["visitor-passes", estateId] });
      toast.success("Visitor pass revoked.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Visitor passes</CardTitle>
        <CardDescription>Active and historical passes for this estate.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading passes…</p>
        ) : passes.length === 0 ? (
          <p className="text-sm text-muted-foreground">No visitor passes found.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Visitor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>QR code</TableHead>
                <TableHead>Valid until</TableHead>
                <TableHead>Entries</TableHead>
                {canRevoke ? <TableHead className="text-right">Action</TableHead> : null}
              </TableRow>
            </TableHeader>
            <TableBody>
              {passes.map((pass) => (
                <TableRow key={pass.id}>
                  <TableCell>
                    <div className="font-medium">{pass.visitor_name}</div>
                    {pass.visitor_phone ? (
                      <div className="text-xs text-muted-foreground">{pass.visitor_phone}</div>
                    ) : null}
                    {pass.purpose ? (
                      <div className="text-xs text-muted-foreground">{pass.purpose}</div>
                    ) : null}
                  </TableCell>
                  <TableCell>
                    <PassStatusBadge status={pass.status} />
                  </TableCell>
                  <TableCell className="font-mono text-xs">{pass.qr_code}</TableCell>
                  <TableCell>{formatDateTime(pass.valid_until)}</TableCell>
                  <TableCell>
                    {pass.entries_used}/{pass.max_entries}
                  </TableCell>
                  {canRevoke ? (
                    <TableCell className="text-right">
                      {pass.status === "active" ? (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={revokeMutation.isPending}
                          onClick={() => revokeMutation.mutate(pass.id)}
                        >
                          Revoke
                        </Button>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </TableCell>
                  ) : null}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function LogsTable({ logs, isLoading }: { logs: VisitorLog[]; isLoading: boolean }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Gate logs</CardTitle>
        <CardDescription>Recent entry and exit events at estate gates.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading gate logs…</p>
        ) : logs.length === 0 ? (
          <p className="text-sm text-muted-foreground">No gate logs found.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Visitor</TableHead>
                <TableHead>Direction</TableHead>
                <TableHead>Gate</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>When</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-medium">{log.visitor_name}</TableCell>
                  <TableCell className="capitalize">{log.direction}</TableCell>
                  <TableCell>{log.gate_name || "—"}</TableCell>
                  <TableCell className="capitalize">{log.verification_method}</TableCell>
                  <TableCell>{formatRelativeTime(log.timestamp)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function BlacklistTable({
  entries,
  isLoading,
}: {
  entries: BlacklistEntry[];
  isLoading: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Blacklist</CardTitle>
        <CardDescription>Individuals denied access to the estate.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading blacklist…</p>
        ) : entries.length === 0 ? (
          <p className="text-sm text-muted-foreground">No active blacklist entries.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Phone</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Description</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {entries.map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell className="font-medium">{entry.full_name}</TableCell>
                  <TableCell>{entry.phone || "—"}</TableCell>
                  <TableCell className="capitalize">{entry.reason.replace("_", " ")}</TableCell>
                  <TableCell className="max-w-xs truncate">{entry.description}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function PassStatusBadge({ status }: { status: VisitorPass["status"] }) {
  const variant =
    status === "active"
      ? "success"
      : status === "expired" || status === "revoked"
        ? "destructive"
        : "secondary";
  return (
    <Badge variant={variant} className="capitalize">
      {status}
    </Badge>
  );
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
