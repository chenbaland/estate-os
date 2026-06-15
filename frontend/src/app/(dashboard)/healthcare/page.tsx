"use client";
import { useQuery } from "@tanstack/react-query";
import { ModulePage } from "@/components/shared/ModulePage";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiRequest } from "@/lib/api";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";
import { formatRelativeTime } from "@/lib/utils";

export default function HealthcarePage() {
  const { data: hospitals, isLoading: hLoading } = useQuery({ queryKey: ["hospitals"], queryFn: () => apiRequest<{ results: any[] }>("/healthcare/hospitals/", { method: "GET" }) });
  const { data: appointments, isLoading: aLoading } = useQuery({ queryKey: ["appointments"], queryFn: () => apiRequest<{ results: any[] }>("/healthcare/appointments/", { method: "GET" }) });
  const apptV: Record<string,any> = { pending:"warning", confirmed:"success", completed:"secondary", cancelled:"destructive" };
  return (
    <ModulePage title="Healthcare" description={MODULE_DESCRIPTIONS.healthcare} iconKey="healthcare" badge="Active">
      <Tabs defaultValue="hospitals" className="space-y-4">
        <TabsList><TabsTrigger value="hospitals">Clinics &amp; hospitals</TabsTrigger><TabsTrigger value="appointments">My appointments</TabsTrigger></TabsList>
        <TabsContent value="hospitals">
          <div className="grid gap-4 md:grid-cols-2">
            {hLoading ? <p className="text-sm text-muted-foreground col-span-2">Loading...</p> : (hospitals?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground col-span-2">No partner facilities listed.</p> :
              (hospitals?.results ?? []).map((h: any) => (
                <Card key={h.id}><CardHeader><CardTitle className="text-base">{h.name}</CardTitle><CardDescription>{h.address || "—"}</CardDescription></CardHeader>
                <CardContent className="space-y-2">
                  {h.phone && <p className="text-sm">{h.phone}</p>}
                  {h.specialties?.length > 0 && <p className="text-sm text-muted-foreground">{h.specialties.join(", ")}</p>}
                  <div className="flex gap-2">{h.is_partner && <Badge>Partner</Badge>}<Badge variant={h.is_active ? "success" : "secondary"}>{h.is_active ? "Open" : "Closed"}</Badge></div>
                </CardContent></Card>))}
          </div>
        </TabsContent>
        <TabsContent value="appointments">
          <Card><CardHeader><CardTitle>Appointments</CardTitle><CardDescription>Your scheduled healthcare appointments.</CardDescription></CardHeader>
          <CardContent>{aLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (appointments?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No appointments.</p> : (
            <Table><TableHeader><TableRow><TableHead>Hospital</TableHead><TableHead>Type</TableHead><TableHead>Status</TableHead><TableHead>Scheduled</TableHead><TableHead>Notes</TableHead></TableRow></TableHeader>
            <TableBody>{(appointments?.results ?? []).map((a: any) => (<TableRow key={a.id}><TableCell className="font-medium">{a.hospital}</TableCell><TableCell className="capitalize">{a.appointment_type?.replace("_"," ")}</TableCell><TableCell><Badge variant={apptV[a.status] ?? "secondary"} className="capitalize">{a.status}</Badge></TableCell><TableCell>{a.scheduled_at ? new Date(a.scheduled_at).toLocaleString() : "—"}</TableCell><TableCell className="max-w-xs truncate">{a.notes || "—"}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </ModulePage>
  );
}
