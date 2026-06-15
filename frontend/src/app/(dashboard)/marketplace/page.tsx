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

export default function MarketplacePage() {
  const { data: vendors, isLoading: vLoading } = useQuery({ queryKey: ["vendors"], queryFn: () => apiRequest<{ results: any[] }>("/marketplace/vendors/", { method: "GET" }) });
  const { data: products, isLoading: pLoading } = useQuery({ queryKey: ["products"], queryFn: () => apiRequest<{ results: any[] }>("/marketplace/products/", { method: "GET" }) });
  const { data: orders, isLoading: oLoading } = useQuery({ queryKey: ["orders"], queryFn: () => apiRequest<{ results: any[] }>("/marketplace/orders/", { method: "GET" }) });
  const orderV: Record<string,any> = { pending:"warning", confirmed:"default", preparing:"warning", ready:"success", delivered:"success", cancelled:"destructive" };
  return (
    <ModulePage title="Marketplace" description={MODULE_DESCRIPTIONS.marketplace} iconKey="marketplace" badge="Active">
      <Tabs defaultValue="vendors" className="space-y-4">
        <TabsList><TabsTrigger value="vendors">Vendors</TabsTrigger><TabsTrigger value="products">Products</TabsTrigger><TabsTrigger value="orders">My orders</TabsTrigger></TabsList>
        <TabsContent value="vendors">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {vLoading ? <p className="text-sm text-muted-foreground col-span-3">Loading...</p> : (vendors?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground col-span-3">No vendors yet.</p> :
              (vendors?.results ?? []).map((v: any) => (
                <Card key={v.id}><CardHeader><CardTitle className="text-base">{v.business_name}</CardTitle><CardDescription>{v.category || "General"}</CardDescription></CardHeader>
                <CardContent className="space-y-1">
                  <div className="flex items-center justify-between"><Badge variant={v.status === "active" ? "success" : "secondary"} className="capitalize">{v.status}</Badge>{v.is_verified && <Badge variant="default">Verified</Badge>}</div>
                  {v.rating_avg && <p className="text-sm text-muted-foreground">Rating: {parseFloat(v.rating_avg).toFixed(1)} ({v.rating_count} reviews)</p>}
                </CardContent></Card>))}
          </div>
        </TabsContent>
        <TabsContent value="products">
          <Card><CardHeader><CardTitle>Available products</CardTitle></CardHeader>
          <CardContent>{pLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (products?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No products listed.</p> : (
            <Table><TableHeader><TableRow><TableHead>Product</TableHead><TableHead>Vendor</TableHead><TableHead>Category</TableHead><TableHead>Price</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
            <TableBody>{(products?.results ?? []).map((p: any) => (<TableRow key={p.id}><TableCell className="font-medium">{p.name}</TableCell><TableCell>{p.vendor}</TableCell><TableCell>{p.category || "—"}</TableCell><TableCell>NGN {parseFloat(p.price || "0").toLocaleString()}</TableCell><TableCell><Badge variant={p.status === "active" ? "success" : "secondary"} className="capitalize">{p.status}</Badge></TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
        <TabsContent value="orders">
          <Card><CardHeader><CardTitle>My orders</CardTitle></CardHeader>
          <CardContent>{oLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (orders?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No orders placed.</p> : (
            <Table><TableHeader><TableRow><TableHead>Order</TableHead><TableHead>Vendor</TableHead><TableHead>Status</TableHead><TableHead>Total</TableHead><TableHead>Placed</TableHead></TableRow></TableHeader>
            <TableBody>{(orders?.results ?? []).map((o: any) => (<TableRow key={o.id}><TableCell className="font-mono text-xs">{o.order_number}</TableCell><TableCell>{o.vendor}</TableCell><TableCell><Badge variant={orderV[o.status] ?? "secondary"} className="capitalize">{o.status}</Badge></TableCell><TableCell>NGN {parseFloat(o.total_amount || "0").toLocaleString()}</TableCell><TableCell>{formatRelativeTime(o.created_at)}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </ModulePage>
  );
}
