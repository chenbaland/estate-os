"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { ModulePage } from "@/components/shared/ModulePage";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/components/ui/toast";
import { useAuth } from "@/hooks/useAuth";
import { hasRole } from "@/lib/auth";
import { apiRequest } from "@/lib/api";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";
import { formatRelativeTime } from "@/lib/utils";

const severityVariant: Record<string, "destructive" | "warning" | "secondary"> = {
  critical: "destructive", high: "destructive", medium: "warning", low: "secondary",
};
const statusVariant: Record<string, "default" | "secondary" | "success" | "warning"> = {
  open: "default", investigating: "warning", resolved: "success", closed: "secondary",
};

export default function SecurityPage() {
  const { roles } = useAuth();
  const qc = useQueryClient();
  const isStaff = hasRole(roles, ["super_admin", "estate_admin", "security_admin", "security_personnel"]);

  const { data: incidents, isLoading: incLoading } = useQuery({
    queryKey: ["security-incidents"],
    queryFn: () => apiRequest<{ results: any[] }>("/security/incidents/", { method: "GET" }),
    enabled: isStaff,
  });
  const { data: sos, isLoading: sosLoading } = useQuery({
    queryKey: ["security-sos"],
    queryFn: () => apiRequest<{ results: any[] }>("/security/sos-alerts/", { method: "GET" }),
    enabled: isStaff,
  });
  const { data: patrols, isLoading: patrolLoading } = useQuery({
    queryKey: ["security-patrols"],
    queryFn: () => apiRequest<{ results: any[] }>("/security/patrol-logs/", { method: "GET" }),
    enabled: isStaff,
  });
  const { data: broadcasts, isLoading: bcLoading } = useQuery({
    queryKey: ["security-broadcasts"],
    queryFn: () => apiRequest<{ results: any[] }>("/security/emergency-broadcasts/", { method: "GET" }),
    enabled: isStaff,
  });

  const [incForm, setIncForm] = useState({ title: "", description: "", category: "theft", severity: "medium", location: "" });
  const incidentMutation = useMutation({
    mutationFn: (data: typeof incForm) => apiRequest("/security/incidents/", { method: "POST", body: data }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["security-incidents"] }); setIncForm({ title: "", description: "", category: "theft", severity: "medium", location: "" }); toast.success("Incident reported."); },
    onError: (e: Error) => toast.error(e.message),
  });

  const ackMutation = useMutation({
    mutationFn: (id: string) => apiRequest(`/security/sos-alerts/${id}/acknowledge/`, { method: "POST", body: {} }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["security-sos"] }); toast.success("Alert acknowledged."); },
    onError: (e: Error) => toast.error(e.message),
  });
  const resolveMutation = useMutation({
    mutationFn: (id: string) => apiRequest(`/security/sos-alerts/${id}/resolve/`, { method: "POST", body: { response_notes: "Resolved by security team" } }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["security-sos"] }); toast.success("Alert resolved."); },
    onError: (e: Error) => toast.error(e.message),
  });

  const [bcForm, setBcForm] = useState({ title: "", message: "", priority: "urgent", channel: "all" });
  const broadcastMutation = useMutation({
    mutationFn: (data: typeof bcForm) => apiRequest("/security/emergency-broadcasts/", { method: "POST", body: data }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["security-broadcasts"] }); setBcForm({ title: "", message: "", priority: "urgent", channel: "all" }); toast.success("Broadcast sent."); },
    onError: (e: Error) => toast.error(e.message),
  });

  const openSOS = (sos?.results ?? []).filter((a: any) => a.status === "active").length;
  const openInc = (incidents?.results ?? []).filter((i: any) => i.status === "open").length;

  return (
    <ModulePage title="Security" description={MODULE_DESCRIPTIONS.security} iconKey="security"
      badge={openSOS > 0 ? `${openSOS} SOS` : openInc > 0 ? `${openInc} open` : "Active"}>
      {!isStaff ? (
        <p className="text-sm text-muted-foreground">Security management is available to security staff and estate administrators.</p>
      ) : (
        <Tabs defaultValue="incidents" className="space-y-4">
          <TabsList>
            <TabsTrigger value="incidents">Incidents {openInc > 0 && <Badge variant="destructive" className="ml-1">{openInc}</Badge>}</TabsTrigger>
            <TabsTrigger value="sos">SOS Alerts {openSOS > 0 && <Badge variant="destructive" className="ml-1">{openSOS}</Badge>}</TabsTrigger>
            <TabsTrigger value="patrols">Patrols</TabsTrigger>
            <TabsTrigger value="broadcasts">Broadcasts</TabsTrigger>
          </TabsList>

          <TabsContent value="incidents" className="space-y-4">
            <Card>
              <CardHeader><CardTitle>Report incident</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="space-y-1"><Label>Title</Label><Input value={incForm.title} onChange={e => setIncForm(p => ({...p, title: e.target.value}))} placeholder="Brief description" /></div>
                  <div className="space-y-1"><Label>Location</Label><Input value={incForm.location} onChange={e => setIncForm(p => ({...p, location: e.target.value}))} placeholder="Gate, block, unit..." /></div>
                  <div className="space-y-1"><Label>Category</Label>
                    <Select value={incForm.category} onValueChange={v => setIncForm(p => ({...p, category: v}))}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>{["theft","vandalism","assault","trespass","fire","flood","noise","other"].map(c => <SelectItem key={c} value={c}>{c.charAt(0).toUpperCase()+c.slice(1)}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1"><Label>Severity</Label>
                    <Select value={incForm.severity} onValueChange={v => setIncForm(p => ({...p, severity: v}))}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>{["low","medium","high","critical"].map(s => <SelectItem key={s} value={s}>{s.charAt(0).toUpperCase()+s.slice(1)}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-1"><Label>Description</Label><Textarea value={incForm.description} onChange={e => setIncForm(p => ({...p, description: e.target.value}))} placeholder="Full details of the incident..." /></div>
                <Button disabled={incidentMutation.isPending || !incForm.title} onClick={() => incidentMutation.mutate(incForm)}>
                  {incidentMutation.isPending ? "Reporting..." : "Report incident"}
                </Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>All incidents</CardTitle><CardDescription>Estate security incidents and their resolution status.</CardDescription></CardHeader>
              <CardContent>
                {incLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (incidents?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No incidents recorded.</p> : (
                  <Table><TableHeader><TableRow><TableHead>Title</TableHead><TableHead>Category</TableHead><TableHead>Severity</TableHead><TableHead>Status</TableHead><TableHead>Location</TableHead><TableHead>When</TableHead></TableRow></TableHeader>
                  <TableBody>{(incidents?.results ?? []).map((inc: any) => (
                    <TableRow key={inc.id}>
                      <TableCell className="font-medium">{inc.title}</TableCell>
                      <TableCell className="capitalize">{inc.category}</TableCell>
                      <TableCell><Badge variant={severityVariant[inc.severity] ?? "secondary"} className="capitalize">{inc.severity}</Badge></TableCell>
                      <TableCell><Badge variant={statusVariant[inc.status] ?? "secondary"} className="capitalize">{inc.status}</Badge></TableCell>
                      <TableCell>{inc.location || "—"}</TableCell>
                      <TableCell>{formatRelativeTime(inc.created_at)}</TableCell>
                    </TableRow>))}</TableBody></Table>)}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sos" className="space-y-4">
            <Card>
              <CardHeader><CardTitle>SOS alerts</CardTitle><CardDescription>Active emergency alerts from residents. Acknowledge then resolve each one.</CardDescription></CardHeader>
              <CardContent>
                {sosLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (sos?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No SOS alerts.</p> : (
                  <Table><TableHeader><TableRow><TableHead>Resident</TableHead><TableHead>Status</TableHead><TableHead>Message</TableHead><TableHead>When</TableHead><TableHead className="text-right">Actions</TableHead></TableRow></TableHeader>
                  <TableBody>{(sos?.results ?? []).map((alert: any) => (
                    <TableRow key={alert.id}>
                      <TableCell className="font-medium">{alert.resident}</TableCell>
                      <TableCell><Badge variant={alert.status === "active" ? "destructive" : alert.status === "acknowledged" ? "warning" : "secondary"} className="capitalize">{alert.status}</Badge></TableCell>
                      <TableCell className="max-w-xs truncate">{alert.message || "—"}</TableCell>
                      <TableCell>{formatRelativeTime(alert.created_at)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {alert.status === "active" && <Button size="sm" variant="outline" disabled={ackMutation.isPending} onClick={() => ackMutation.mutate(alert.id)}>Acknowledge</Button>}
                          {alert.status === "acknowledged" && <Button size="sm" disabled={resolveMutation.isPending} onClick={() => resolveMutation.mutate(alert.id)}>Resolve</Button>}
                          {alert.status === "resolved" && <span className="text-xs text-muted-foreground">Resolved</span>}
                        </div>
                      </TableCell>
                    </TableRow>))}</TableBody></Table>)}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="patrols">
            <Card>
              <CardHeader><CardTitle>Patrol logs</CardTitle><CardDescription>Security officer patrol activity and checkpoint records.</CardDescription></CardHeader>
              <CardContent>
                {patrolLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (patrols?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No patrol logs.</p> : (
                  <Table><TableHeader><TableRow><TableHead>Officer</TableHead><TableHead>Zone</TableHead><TableHead>Status</TableHead><TableHead>Started</TableHead><TableHead>Ended</TableHead><TableHead>Notes</TableHead></TableRow></TableHeader>
                  <TableBody>{(patrols?.results ?? []).map((p: any) => (
                    <TableRow key={p.id}>
                      <TableCell className="font-medium">{p.officer}</TableCell>
                      <TableCell>{p.zone || "—"}</TableCell>
                      <TableCell><Badge variant={p.status === "completed" ? "success" : "secondary"} className="capitalize">{p.status}</Badge></TableCell>
                      <TableCell>{p.started_at ? formatRelativeTime(p.started_at) : "—"}</TableCell>
                      <TableCell>{p.ended_at ? formatRelativeTime(p.ended_at) : "—"}</TableCell>
                      <TableCell className="max-w-xs truncate">{p.notes || "—"}</TableCell>
                    </TableRow>))}</TableBody></Table>)}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="broadcasts" className="space-y-4">
            <Card>
              <CardHeader><CardTitle>Send emergency broadcast</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="space-y-1"><Label>Title</Label><Input value={bcForm.title} onChange={e => setBcForm(p => ({...p, title: e.target.value}))} placeholder="Alert title" /></div>
                  <div className="space-y-1"><Label>Priority</Label>
                    <Select value={bcForm.priority} onValueChange={v => setBcForm(p => ({...p, priority: v}))}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>{["info","warning","urgent","critical"].map(p => <SelectItem key={p} value={p}>{p.charAt(0).toUpperCase()+p.slice(1)}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1"><Label>Channel</Label>
                    <Select value={bcForm.channel} onValueChange={v => setBcForm(p => ({...p, channel: v}))}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>{["all","push","sms","email"].map(c => <SelectItem key={c} value={c}>{c.charAt(0).toUpperCase()+c.slice(1)}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1 sm:col-span-2"><Label>Message</Label><Textarea value={bcForm.message} onChange={e => setBcForm(p => ({...p, message: e.target.value}))} placeholder="Emergency message to all residents..." /></div>
                </div>
                <Button variant="destructive" disabled={broadcastMutation.isPending || !bcForm.title || !bcForm.message} onClick={() => broadcastMutation.mutate(bcForm)}>
                  {broadcastMutation.isPending ? "Sending..." : "Send broadcast"}
                </Button>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Recent broadcasts</CardTitle></CardHeader>
              <CardContent>
                {bcLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (broadcasts?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No broadcasts sent.</p> : (
                  <Table><TableHeader><TableRow><TableHead>Title</TableHead><TableHead>Priority</TableHead><TableHead>Channel</TableHead><TableHead>Sent by</TableHead><TableHead>When</TableHead></TableRow></TableHeader>
                  <TableBody>{(broadcasts?.results ?? []).map((b: any) => (
                    <TableRow key={b.id}>
                      <TableCell className="font-medium">{b.title}</TableCell>
                      <TableCell><Badge variant={b.priority === "critical" || b.priority === "urgent" ? "destructive" : "secondary"} className="capitalize">{b.priority}</Badge></TableCell>
                      <TableCell className="capitalize">{b.channel}</TableCell>
                      <TableCell>{b.sent_by}</TableCell>
                      <TableCell>{formatRelativeTime(b.created_at)}</TableCell>
                    </TableRow>))}</TableBody></Table>)}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </ModulePage>
  );
}
