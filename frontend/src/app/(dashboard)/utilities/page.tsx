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

export default function UtilitiesPage() {
  const { data: accounts, isLoading: accLoading } = useQuery({ queryKey: ["utility-accounts"], queryFn: () => apiRequest<{ results: any[] }>("/utilities/accounts/", { method: "GET" }) });
  const { data: txns, isLoading: txnLoading } = useQuery({ queryKey: ["utility-transactions"], queryFn: () => apiRequest<{ results: any[] }>("/utilities/transactions/", { method: "GET" }) });
  const txnV: Record<string,any> = { pending:"warning", completed:"success", failed:"destructive", reversed:"secondary" };
  return (
    <ModulePage title="Utilities" description={MODULE_DESCRIPTIONS.utilities} iconKey="utilities" badge="Active">
      <Tabs defaultValue="accounts" className="space-y-4">
        <TabsList><TabsTrigger value="accounts">Utility accounts</TabsTrigger><TabsTrigger value="transactions">Transactions</TabsTrigger></TabsList>
        <TabsContent value="accounts">
          <div className="grid gap-4 md:grid-cols-2">
            {accLoading ? <p className="text-sm text-muted-foreground col-span-2">Loading...</p> : (accounts?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground col-span-2">No utility accounts.</p> :
              (accounts?.results ?? []).map((a: any) => (
                <Card key={a.id}><CardHeader><CardTitle className="text-base capitalize">{a.utility_type?.replace("_"," ")} — {a.provider_name || "Provider"}</CardTitle><CardDescription>Account {a.account_number} · Meter {a.meter_number || "—"}</CardDescription></CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm"><span className="text-muted-foreground">Balance</span><span className="font-medium">NGN {parseFloat(a.current_balance || "0").toLocaleString()}</span></div>
                  <div className="flex justify-between text-sm"><span className="text-muted-foreground">Status</span><Badge variant={a.status === "active" ? "success" : "secondary"} className="capitalize">{a.status}</Badge></div>
                  {a.last_reading && <div className="flex justify-between text-sm"><span className="text-muted-foreground">Last reading</span><span>{a.last_reading} units</span></div>}
                </CardContent></Card>))}
          </div>
        </TabsContent>
        <TabsContent value="transactions">
          <Card><CardHeader><CardTitle>Transaction history</CardTitle><CardDescription>Utility top-ups and purchases.</CardDescription></CardHeader>
          <CardContent>{txnLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (txns?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No transactions yet.</p> : (
            <Table><TableHeader><TableRow><TableHead>Type</TableHead><TableHead>Utility</TableHead><TableHead>Amount</TableHead><TableHead>Status</TableHead><TableHead>When</TableHead></TableRow></TableHeader>
            <TableBody>{(txns?.results ?? []).map((t: any) => (<TableRow key={t.id}><TableCell className="capitalize">{t.transaction_type?.replace("_"," ")}</TableCell><TableCell>{t.utility_account}</TableCell><TableCell>NGN {parseFloat(t.amount || "0").toLocaleString()}</TableCell><TableCell><Badge variant={txnV[t.status] ?? "secondary"} className="capitalize">{t.status}</Badge></TableCell><TableCell>{formatRelativeTime(t.created_at)}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </ModulePage>
  );
}
