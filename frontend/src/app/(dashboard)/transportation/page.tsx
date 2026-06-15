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
import { toast } from "@/components/ui/toast";
import { apiRequest } from "@/lib/api";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";
import { formatRelativeTime } from "@/lib/utils";

export default function TransportationPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["ride-requests"], queryFn: () => apiRequest<{ results: any[] }>("/transportation/ride-requests/", { method: "GET" }) });
  const [form, setForm] = useState({ pickup_address: "", dropoff_address: "", ride_type: "standard" });
  const rideV: Record<string,any> = { requested:"warning", assigned:"default", in_progress:"default", completed:"success", cancelled:"secondary" };

  const createMutation = useMutation({
    mutationFn: (data: typeof form) => apiRequest("/transportation/ride-requests/", { method: "POST", body: data }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["ride-requests"] }); setForm({ pickup_address: "", dropoff_address: "", ride_type: "standard" }); toast.success("Ride requested."); },
    onError: (e: Error) => toast.error(e.message),
  });

  const active = (data?.results ?? []).filter((r: any) => ["requested","assigned","in_progress"].includes(r.status)).length;
  return (
    <ModulePage title="Transportation" description={MODULE_DESCRIPTIONS.transportation} iconKey="transportation" badge={active > 0 ? `${active} active` : "Active"}>
      <Tabs defaultValue="history" className="space-y-4">
        <TabsList><TabsTrigger value="history">Ride history</TabsTrigger><TabsTrigger value="new">Request ride</TabsTrigger></TabsList>
        <TabsContent value="history">
          <Card><CardHeader><CardTitle>Ride requests</CardTitle><CardDescription>Your estate shuttle and ride requests.</CardDescription></CardHeader>
          <CardContent>{isLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (data?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No rides requested yet.</p> : (
            <Table><TableHeader><TableRow><TableHead>Type</TableHead><TableHead>Pickup</TableHead><TableHead>Dropoff</TableHead><TableHead>Status</TableHead><TableHead>Driver</TableHead><TableHead>When</TableHead></TableRow></TableHeader>
            <TableBody>{(data?.results ?? []).map((r: any) => (<TableRow key={r.id}><TableCell className="capitalize">{r.ride_type?.replace("_"," ")}</TableCell><TableCell className="max-w-[140px] truncate">{r.pickup_address}</TableCell><TableCell className="max-w-[140px] truncate">{r.dropoff_address}</TableCell><TableCell><Badge variant={rideV[r.status] ?? "secondary"} className="capitalize">{r.status?.replace("_"," ")}</Badge></TableCell><TableCell>{r.driver_name || "—"}</TableCell><TableCell>{formatRelativeTime(r.created_at)}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
        <TabsContent value="new">
          <Card><CardHeader><CardTitle>Request a ride</CardTitle><CardDescription>Book an estate shuttle or external ride service.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="space-y-1"><Label>Pickup address</Label><Input value={form.pickup_address} onChange={e => setForm(p => ({...p, pickup_address: e.target.value}))} placeholder="Unit A-101 or estate gate" /></div>
              <div className="space-y-1"><Label>Dropoff address</Label><Input value={form.dropoff_address} onChange={e => setForm(p => ({...p, dropoff_address: e.target.value}))} placeholder="Destination" /></div>
              <div className="space-y-1"><Label>Ride type</Label>
                <Select value={form.ride_type} onValueChange={v => setForm(p => ({...p, ride_type: v}))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{["standard","premium","shared","shuttle"].map(t => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase()+t.slice(1)}</SelectItem>)}</SelectContent>
                </Select>
              </div>
            </div>
            <Button disabled={createMutation.isPending || !form.pickup_address || !form.dropoff_address} onClick={() => createMutation.mutate(form)}>
              {createMutation.isPending ? "Requesting..." : "Request ride"}
            </Button>
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </ModulePage>
  );
}
