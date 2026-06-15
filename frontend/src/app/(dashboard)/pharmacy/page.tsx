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

export default function PharmacyPage() {
  const { data: prescriptions, isLoading: rxLoading } = useQuery({ queryKey: ["prescriptions"], queryFn: () => apiRequest<{ results: any[] }>("/pharmacy/prescriptions/", { method: "GET" }) });
  const { data: orders, isLoading: oLoading } = useQuery({ queryKey: ["medication-orders"], queryFn: () => apiRequest<{ results: any[] }>("/pharmacy/medication-orders/", { method: "GET" }) });
  const rxV: Record<string,any> = { pending:"warning", verified:"success", dispensed:"secondary", expired:"destructive" };
  const orderV: Record<string,any> = { pending:"warning", processing:"warning", ready:"success", delivered:"secondary", cancelled:"destructive" };
  return (
    <ModulePage title="Pharmacy" description={MODULE_DESCRIPTIONS.pharmacy} iconKey="pharmacy" badge="Active">
      <Tabs defaultValue="prescriptions" className="space-y-4">
        <TabsList><TabsTrigger value="prescriptions">Prescriptions</TabsTrigger><TabsTrigger value="orders">Medication orders</TabsTrigger></TabsList>
        <TabsContent value="prescriptions">
          <Card><CardHeader><CardTitle>Prescriptions</CardTitle><CardDescription>Upload prescriptions to order medications for delivery.</CardDescription></CardHeader>
          <CardContent>{rxLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (prescriptions?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No prescriptions uploaded.</p> : (
            <Table><TableHeader><TableRow><TableHead>Ref</TableHead><TableHead>Doctor</TableHead><TableHead>Hospital</TableHead><TableHead>Status</TableHead><TableHead>Issued</TableHead><TableHead>Expires</TableHead></TableRow></TableHeader>
            <TableBody>{(prescriptions?.results ?? []).map((rx: any) => (<TableRow key={rx.id}><TableCell className="font-mono text-xs">{rx.prescription_number}</TableCell><TableCell>{rx.doctor_name || "—"}</TableCell><TableCell>{rx.hospital_name || "—"}</TableCell><TableCell><Badge variant={rxV[rx.status] ?? "secondary"} className="capitalize">{rx.status}</Badge></TableCell><TableCell>{rx.issued_date ? new Date(rx.issued_date).toLocaleDateString() : "—"}</TableCell><TableCell>{rx.expiry_date ? new Date(rx.expiry_date).toLocaleDateString() : "—"}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
        <TabsContent value="orders">
          <Card><CardHeader><CardTitle>Medication orders</CardTitle></CardHeader>
          <CardContent>{oLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (orders?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No medication orders.</p> : (
            <Table><TableHeader><TableRow><TableHead>Prescription</TableHead><TableHead>Status</TableHead><TableHead>Total</TableHead><TableHead>Ordered</TableHead></TableRow></TableHeader>
            <TableBody>{(orders?.results ?? []).map((o: any) => (<TableRow key={o.id}><TableCell>{o.prescription}</TableCell><TableCell><Badge variant={orderV[o.status] ?? "secondary"} className="capitalize">{o.status}</Badge></TableCell><TableCell>{o.total_amount ? `NGN ${parseFloat(o.total_amount).toLocaleString()}` : "—"}</TableCell><TableCell>{formatRelativeTime(o.created_at)}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </ModulePage>
  );
}
