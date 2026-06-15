"use client";
import { useQuery } from "@tanstack/react-query";
import { ModulePage } from "@/components/shared/ModulePage";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiRequest } from "@/lib/api";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";

export default function ParkingPage() {
  const { data: slots, isLoading: slotsLoading } = useQuery({ queryKey: ["parking-slots"], queryFn: () => apiRequest<{ results: any[] }>("/parking/slots/", { method: "GET" }) });
  const { data: permits, isLoading: permitsLoading } = useQuery({ queryKey: ["parking-permits"], queryFn: () => apiRequest<{ results: any[] }>("/parking/permits/", { method: "GET" }) });
  const { data: ev, isLoading: evLoading } = useQuery({ queryKey: ["ev-sessions"], queryFn: () => apiRequest<{ results: any[] }>("/parking/ev-sessions/", { method: "GET" }) });
  const slotV: Record<string,any> = { available:"success", occupied:"default", reserved:"warning", maintenance:"secondary" };
  const permitV: Record<string,any> = { active:"success", expired:"secondary", suspended:"destructive" };
  return (
    <ModulePage title="Parking" description={MODULE_DESCRIPTIONS.parking} iconKey="parking" badge="Active">
      <Tabs defaultValue="slots" className="space-y-4">
        <TabsList><TabsTrigger value="slots">Slots</TabsTrigger><TabsTrigger value="permits">Permits</TabsTrigger><TabsTrigger value="ev">EV Charging</TabsTrigger></TabsList>
        <TabsContent value="slots">
          <Card><CardHeader><CardTitle>Parking slots</CardTitle><CardDescription>All estate parking slots and their current status.</CardDescription></CardHeader>
          <CardContent>{slotsLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (slots?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No slots found.</p> : (
            <Table><TableHeader><TableRow><TableHead>Slot</TableHead><TableHead>Type</TableHead><TableHead>Block</TableHead><TableHead>Status</TableHead><TableHead>EV</TableHead><TableHead>Rate/mo</TableHead></TableRow></TableHeader>
            <TableBody>{(slots?.results ?? []).map((s: any) => (<TableRow key={s.id}><TableCell className="font-medium">{s.slot_number}</TableCell><TableCell className="capitalize">{s.slot_type?.replace("_"," ")}</TableCell><TableCell>{s.block || "—"}</TableCell><TableCell><Badge variant={slotV[s.status] ?? "secondary"} className="capitalize">{s.status}</Badge></TableCell><TableCell>{s.has_ev_charger ? "Yes" : "—"}</TableCell><TableCell>{s.monthly_rate ? `NGN ${s.monthly_rate}` : "—"}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
        <TabsContent value="permits">
          <Card><CardHeader><CardTitle>Parking permits</CardTitle></CardHeader>
          <CardContent>{permitsLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (permits?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No permits found.</p> : (
            <Table><TableHeader><TableRow><TableHead>Permit</TableHead><TableHead>Slot</TableHead><TableHead>Vehicle</TableHead><TableHead>Status</TableHead><TableHead>Expires</TableHead></TableRow></TableHeader>
            <TableBody>{(permits?.results ?? []).map((p: any) => (<TableRow key={p.id}><TableCell className="font-mono text-xs">{p.permit_number}</TableCell><TableCell>{p.slot}</TableCell><TableCell>{p.vehicle}</TableCell><TableCell><Badge variant={permitV[p.status] ?? "secondary"} className="capitalize">{p.status}</Badge></TableCell><TableCell>{p.end_date ? new Date(p.end_date).toLocaleDateString() : "—"}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
        <TabsContent value="ev">
          <Card><CardHeader><CardTitle>EV charging sessions</CardTitle></CardHeader>
          <CardContent>{evLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (ev?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No EV sessions found.</p> : (
            <Table><TableHeader><TableRow><TableHead>Slot</TableHead><TableHead>Vehicle</TableHead><TableHead>Status</TableHead><TableHead>Energy (kWh)</TableHead><TableHead>Cost</TableHead></TableRow></TableHeader>
            <TableBody>{(ev?.results ?? []).map((s: any) => (<TableRow key={s.id}><TableCell>{s.slot}</TableCell><TableCell>{s.vehicle}</TableCell><TableCell><Badge variant={s.status === "active" ? "success" : "secondary"} className="capitalize">{s.status}</Badge></TableCell><TableCell>{s.energy_kwh ?? "—"}</TableCell><TableCell>{s.total_cost ? `NGN ${s.total_cost}` : "—"}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </ModulePage>
  );
}
