"use client";
import { useQuery } from "@tanstack/react-query";
import { ModulePage } from "@/components/shared/ModulePage";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { apiRequest } from "@/lib/api";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";
import { formatRelativeTime } from "@/lib/utils";

const statusV: Record<string,any> = { expected:"secondary", received:"default", notified:"warning", collected:"success", returned:"secondary", lost:"destructive" };
export default function PackagesPage() {
  const { data, isLoading } = useQuery({ queryKey: ["packages"], queryFn: () => apiRequest<{ results: any[] }>("/packages/packages/", { method: "GET" }) });
  const awaiting = (data?.results ?? []).filter((p: any) => p.status === "received" || p.status === "notified").length;
  return (
    <ModulePage title="Packages" description={MODULE_DESCRIPTIONS.packages} iconKey="packages" badge={awaiting > 0 ? `${awaiting} awaiting pickup` : "Active"}>
      <Card>
        <CardHeader><CardTitle>Package log</CardTitle><CardDescription>Incoming deliveries and their pickup status.</CardDescription></CardHeader>
        <CardContent>
          {isLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (data?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No packages recorded.</p> : (
            <Table><TableHeader><TableRow><TableHead>Tracking</TableHead><TableHead>Type</TableHead><TableHead>Carrier</TableHead><TableHead>Sender</TableHead><TableHead>Status</TableHead><TableHead>Received</TableHead><TableHead>Collected</TableHead></TableRow></TableHeader>
            <TableBody>{(data?.results ?? []).map((p: any) => (
              <TableRow key={p.id}>
                <TableCell className="font-mono text-xs">{p.tracking_number || "—"}</TableCell>
                <TableCell className="capitalize">{p.package_type?.replace("_"," ")}</TableCell>
                <TableCell>{p.carrier || "—"}</TableCell>
                <TableCell>{p.sender_name || "—"}</TableCell>
                <TableCell><Badge variant={statusV[p.status] ?? "secondary"} className="capitalize">{p.status}</Badge></TableCell>
                <TableCell>{p.received_at ? formatRelativeTime(p.received_at) : "—"}</TableCell>
                <TableCell>{p.collected_at ? formatRelativeTime(p.collected_at) : "—"}</TableCell>
              </TableRow>))}</TableBody></Table>)}
        </CardContent>
      </Card>
    </ModulePage>
  );
}
