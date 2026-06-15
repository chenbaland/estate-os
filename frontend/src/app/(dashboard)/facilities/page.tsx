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

export default function FacilitiesPage() {
  const { data: facilities, isLoading: facLoading } = useQuery({ queryKey: ["facilities"], queryFn: () => apiRequest<{ results: any[] }>("/facilities/facilities/", { method: "GET" }) });
  const { data: bookings, isLoading: bookLoading } = useQuery({ queryKey: ["bookings"], queryFn: () => apiRequest<{ results: any[] }>("/facilities/bookings/", { method: "GET" }) });
  const statusV: Record<string,any> = { pending:"warning", confirmed:"success", cancelled:"secondary", completed:"secondary" };
  return (
    <ModulePage title="Facilities" description={MODULE_DESCRIPTIONS.facilities} iconKey="facilities" badge="Active">
      <Tabs defaultValue="facilities" className="space-y-4">
        <TabsList><TabsTrigger value="facilities">Facilities</TabsTrigger><TabsTrigger value="bookings">My bookings</TabsTrigger></TabsList>
        <TabsContent value="facilities">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {facLoading ? <p className="text-sm text-muted-foreground col-span-3">Loading...</p> : (facilities?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground col-span-3">No facilities available.</p> :
              (facilities?.results ?? []).map((f: any) => (
                <Card key={f.id}>
                  <CardHeader><CardTitle className="text-base">{f.name}</CardTitle><CardDescription>{f.facility_type?.replace("_"," ")} · {f.location || "Estate"}</CardDescription></CardHeader>
                  <CardContent className="space-y-2">
                    {f.capacity && <p className="text-sm text-muted-foreground">Capacity: {f.capacity}</p>}
                    {f.hourly_rate && <p className="text-sm text-muted-foreground">{f.currency || "NGN"} {f.hourly_rate}/hr</p>}
                    <Badge variant={f.is_active ? "default" : "secondary"}>{f.is_active ? "Available" : "Unavailable"}</Badge>
                  </CardContent>
                </Card>))}
          </div>
        </TabsContent>
        <TabsContent value="bookings">
          <Card>
            <CardHeader><CardTitle>Bookings</CardTitle><CardDescription>Your facility reservations.</CardDescription></CardHeader>
            <CardContent>
              {bookLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (bookings?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No bookings found.</p> : (
                <Table><TableHeader><TableRow><TableHead>Facility</TableHead><TableHead>Status</TableHead><TableHead>From</TableHead><TableHead>To</TableHead><TableHead>Amount</TableHead></TableRow></TableHeader>
                <TableBody>{(bookings?.results ?? []).map((b: any) => (
                  <TableRow key={b.id}>
                    <TableCell className="font-medium">{b.facility}</TableCell>
                    <TableCell><Badge variant={statusV[b.status] ?? "secondary"} className="capitalize">{b.status}</Badge></TableCell>
                    <TableCell>{b.start_time ? new Date(b.start_time).toLocaleString() : "—"}</TableCell>
                    <TableCell>{b.end_time ? new Date(b.end_time).toLocaleString() : "—"}</TableCell>
                    <TableCell>{b.total_amount ? `${b.currency || "NGN"} ${b.total_amount}` : "—"}</TableCell>
                  </TableRow>))}</TableBody></Table>)}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </ModulePage>
  );
}
