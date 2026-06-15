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

const priorityVariant: Record<string, any> = {
  low: "secondary", medium: "warning", high: "destructive", urgent: "destructive",
};
const statusVariant: Record<string, any> = {
  open: "default", in_progress: "warning", resolved: "success", closed: "secondary", cancelled: "secondary",
};

export default function MaintenancePage() {
  const { roles } = useAuth();
  const qc = useQueryClient();
  // Staff can view and manage all tickets; residents submit and track their own
  const isStaff = hasRole(roles, ["super_admin", "estate_admin", "facility_admin", "technician"]);

  const { data: tickets, isLoading } = useQuery({
    queryKey: ["maintenance-tickets"],
    queryFn: () => apiRequest<{ results: any[] }>("/maintenance/tickets/", { method: "GET" }),
  });

  const [form, setForm] = useState({
    title: "", description: "", category: "plumbing", priority: "medium", location: "",
  });
  const [selectedTicket, setSelectedTicket] = useState<any>(null);
  const [commentText, setCommentText] = useState("");

  const { data: comments, refetch: refetchComments, isLoading: commentsLoading } = useQuery({
    queryKey: ["ticket-comments", selectedTicket?.id],
    queryFn: () => apiRequest<{ results: any[] }>(`/maintenance/tickets/${selectedTicket.id}/comments/`, { method: "GET" }),
    enabled: !!selectedTicket,
  });

  const createMutation = useMutation({
    mutationFn: (data: typeof form) => apiRequest("/maintenance/tickets/", { method: "POST", body: data }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["maintenance-tickets"] });
      setForm({ title: "", description: "", category: "plumbing", priority: "medium", location: "" });
      toast.success("Maintenance request submitted.");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const commentMutation = useMutation({
    mutationFn: ({ id, body }: { id: string; body: string }) =>
      apiRequest(`/maintenance/tickets/${id}/comments/`, { method: "POST", body: { body, is_internal: false } }),
    onSuccess: () => {
      refetchComments();
      setCommentText("");
      toast.success("Comment added.");
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const openCount = (tickets?.results ?? []).filter((t: any) =>
    ["open", "in_progress"].includes(t.status)
  ).length;

  const CATEGORIES = ["plumbing", "electrical", "hvac", "structural", "appliance", "security", "cleaning", "landscaping", "other"];
  const PRIORITIES = ["low", "medium", "high", "urgent"];

  return (
    <ModulePage
      title="Maintenance"
      description={MODULE_DESCRIPTIONS.maintenance}
      iconKey="maintenance"
      badge={openCount > 0 ? `${openCount} open` : "Active"}
    >
      <Tabs defaultValue={isStaff ? "tickets" : "new"} className="space-y-4">
        <TabsList>
          {isStaff && <TabsTrigger value="tickets">All tickets</TabsTrigger>}
          <TabsTrigger value="new">Submit request</TabsTrigger>
          {!isStaff && <TabsTrigger value="mine">My requests</TabsTrigger>}
          {selectedTicket && <TabsTrigger value="detail"># {selectedTicket.ticket_number}</TabsTrigger>}
        </TabsList>

        {/* Staff: see all tickets */}
        {isStaff && (
          <TabsContent value="tickets">
            <Card>
              <CardHeader>
                <CardTitle>All maintenance tickets</CardTitle>
                <CardDescription>View and manage all estate maintenance requests.</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <p className="text-sm text-muted-foreground">Loading tickets...</p>
                ) : (tickets?.results ?? []).length === 0 ? (
                  <p className="text-sm text-muted-foreground">No tickets yet.</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Ticket</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead>Priority</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Assigned</TableHead>
                        <TableHead>Submitted</TableHead>
                        <TableHead></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {(tickets?.results ?? []).map((t: any) => (
                        <TableRow key={t.id}>
                          <TableCell className="font-mono text-xs">{t.ticket_number}</TableCell>
                          <TableCell className="font-medium max-w-[180px] truncate">{t.title}</TableCell>
                          <TableCell className="capitalize">{t.category?.replace("_", " ")}</TableCell>
                          <TableCell>
                            <Badge variant={priorityVariant[t.priority] ?? "secondary"} className="capitalize">
                              {t.priority}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={statusVariant[t.status] ?? "secondary"} className="capitalize">
                              {t.status?.replace("_", " ")}
                            </Badge>
                          </TableCell>
                          <TableCell>{t.assigned_to ?? "—"}</TableCell>
                          <TableCell>{formatRelativeTime(t.created_at)}</TableCell>
                          <TableCell>
                            <Button size="sm" variant="ghost" onClick={() => setSelectedTicket(t)}>
                              View
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Everyone: submit a request */}
        <TabsContent value="new">
          <Card>
            <CardHeader>
              <CardTitle>Submit maintenance request</CardTitle>
              <CardDescription>
                Describe the issue. Our team will be assigned and you'll be notified on updates.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1">
                  <Label>Title</Label>
                  <Input
                    value={form.title}
                    onChange={e => setForm(p => ({ ...p, title: e.target.value }))}
                    placeholder="e.g. Leaking pipe in bathroom"
                  />
                </div>
                <div className="space-y-1">
                  <Label>Location</Label>
                  <Input
                    value={form.location}
                    onChange={e => setForm(p => ({ ...p, location: e.target.value }))}
                    placeholder="Unit, block, floor..."
                  />
                </div>
                <div className="space-y-1">
                  <Label>Category</Label>
                  <Select value={form.category} onValueChange={v => setForm(p => ({ ...p, category: v }))}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {CATEGORIES.map(c => (
                        <SelectItem key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label>Priority</Label>
                  <Select value={form.priority} onValueChange={v => setForm(p => ({ ...p, priority: v }))}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {PRIORITIES.map(p => (
                        <SelectItem key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-1">
                <Label>Description</Label>
                <Textarea
                  value={form.description}
                  onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
                  placeholder="Full details — when it started, severity, safety concern..."
                />
              </div>
              <Button
                disabled={createMutation.isPending || !form.title}
                onClick={() => createMutation.mutate(form)}
              >
                {createMutation.isPending ? "Submitting..." : "Submit request"}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Residents: see their own tickets */}
        {!isStaff && (
          <TabsContent value="mine">
            <Card>
              <CardHeader>
                <CardTitle>My requests</CardTitle>
                <CardDescription>Track your submitted maintenance requests.</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <p className="text-sm text-muted-foreground">Loading...</p>
                ) : (tickets?.results ?? []).length === 0 ? (
                  <p className="text-sm text-muted-foreground">No requests submitted yet.</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Ticket</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Priority</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Submitted</TableHead>
                        <TableHead></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {(tickets?.results ?? []).map((t: any) => (
                        <TableRow key={t.id}>
                          <TableCell className="font-mono text-xs">{t.ticket_number}</TableCell>
                          <TableCell className="font-medium max-w-[200px] truncate">{t.title}</TableCell>
                          <TableCell>
                            <Badge variant={priorityVariant[t.priority] ?? "secondary"} className="capitalize">
                              {t.priority}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={statusVariant[t.status] ?? "secondary"} className="capitalize">
                              {t.status?.replace("_", " ")}
                            </Badge>
                          </TableCell>
                          <TableCell>{formatRelativeTime(t.created_at)}</TableCell>
                          <TableCell>
                            <Button size="sm" variant="ghost" onClick={() => setSelectedTicket(t)}>
                              View
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Detail panel: available to all after clicking a ticket */}
        {selectedTicket && (
          <TabsContent value="detail" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <CardTitle>{selectedTicket.title}</CardTitle>
                    <CardDescription>{selectedTicket.ticket_number} · {selectedTicket.category}</CardDescription>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <Badge variant={priorityVariant[selectedTicket.priority] ?? "secondary"} className="capitalize">
                      {selectedTicket.priority}
                    </Badge>
                    <Badge variant={statusVariant[selectedTicket.status] ?? "secondary"} className="capitalize">
                      {selectedTicket.status?.replace("_", " ")}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm">{selectedTicket.description}</p>
                {selectedTicket.location && (
                  <p className="text-sm text-muted-foreground">Location: {selectedTicket.location}</p>
                )}
                {selectedTicket.assigned_to && (
                  <p className="text-sm text-muted-foreground">Assigned to: {selectedTicket.assigned_to}</p>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Comments & updates</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {commentsLoading ? (
                  <p className="text-sm text-muted-foreground">Loading comments...</p>
                ) : (comments?.results ?? []).length === 0 ? (
                  <p className="text-sm text-muted-foreground">No comments yet.</p>
                ) : (
                  <div className="space-y-3">
                    {(comments?.results ?? []).map((c: any) => (
                      <div key={c.id} className="rounded-lg border p-3">
                        <p className="text-xs text-muted-foreground mb-1">
                          {c.author} · {formatRelativeTime(c.created_at)}
                        </p>
                        <p className="text-sm">{c.body}</p>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex gap-2 pt-2 items-end">
                  <Textarea
                    placeholder="Add a comment or update..."
                    value={commentText}
                    onChange={e => setCommentText(e.target.value)}
                    className="min-h-[60px] flex-1"
                  />
                  <Button
                    disabled={commentMutation.isPending || !commentText.trim()}
                    onClick={() => commentMutation.mutate({ id: selectedTicket.id, body: commentText })}
                  >
                    Post
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </ModulePage>
  );
}
