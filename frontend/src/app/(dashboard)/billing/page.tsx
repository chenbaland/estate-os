"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ModulePage } from "@/components/shared/ModulePage";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/toast";
import { useAuth } from "@/hooks/useAuth";
import { useEstate } from "@/hooks/useEstate";
import { hasRole } from "@/lib/auth";
import { api, getEstateId } from "@/lib/api";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";
import { formatCurrency } from "@/lib/utils";
import type { DebtRecord, Invoice, Payment } from "@/types";

export default function BillingPage() {
  const { roles, memberships } = useAuth();
  const { currentEstate, isLoading: estateLoading } = useEstate();
  const estateId = currentEstate?.id ?? getEstateId();
  const isFinanceView = hasRole(roles, [
    "super_admin",
    "estate_admin",
    "finance_admin",
  ]);
  const residentProfileId = memberships.find(
    (m) => m.estate_id === estateId && m.status === "active",
  )?.resident_profile_id;

  const { data: invoices = [], isLoading: invoicesLoading } = useQuery({
    queryKey: ["billing-invoices", estateId, residentProfileId, isFinanceView],
    queryFn: async () => {
      const params = isFinanceView
        ? undefined
        : residentProfileId
          ? { resident: residentProfileId }
          : undefined;
      const response = await api.getInvoices(params);
      return response.results;
    },
    enabled: Boolean(estateId) && (isFinanceView || Boolean(residentProfileId)),
  });

  const { data: payments = [], isLoading: paymentsLoading } = useQuery({
    queryKey: ["billing-payments", estateId],
    queryFn: async () => {
      const response = await api.getPayments();
      return response.results;
    },
    enabled: Boolean(estateId) && isFinanceView,
  });

  const { data: debts = [], isLoading: debtsLoading } = useQuery({
    queryKey: ["billing-debts", estateId],
    queryFn: async () => {
      const response = await api.getDebtRecords();
      return response.results;
    },
    enabled: Boolean(estateId) && isFinanceView,
  });

  const overdueCount = invoices.filter((inv) => inv.status === "overdue").length;
  const badge =
    overdueCount > 0 ? `${overdueCount} overdue` : invoices.length > 0 ? "Live" : "Active";

  if (estateLoading || !estateId) {
    return (
      <ModulePage
        title="Billing"
        description={MODULE_DESCRIPTIONS.billing}
        iconKey="billing"
        badge="Loading"
      >
        <p className="text-sm text-muted-foreground">Loading estate context…</p>
      </ModulePage>
    );
  }

  if (!isFinanceView && !residentProfileId) {
    return (
      <ModulePage
        title="Billing"
        description={MODULE_DESCRIPTIONS.billing}
        iconKey="billing"
        badge="Active"
      >
        <p className="text-sm text-muted-foreground">
          Billing is available to residents with an active unit assignment or finance administrators.
        </p>
      </ModulePage>
    );
  }

  return (
    <ModulePage
      title="Billing"
      description={MODULE_DESCRIPTIONS.billing}
      iconKey="billing"
      badge={badge}
    >
      <Tabs defaultValue="invoices" className="space-y-4">
        <TabsList>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
          {isFinanceView ? (
            <>
              <TabsTrigger value="payments">Payments</TabsTrigger>
              <TabsTrigger value="debts">Debts</TabsTrigger>
            </>
          ) : null}
        </TabsList>

        <TabsContent value="invoices">
          <InvoicesTable
            invoices={invoices}
            isLoading={invoicesLoading}
            canPay={!isFinanceView}
            estateId={estateId}
          />
        </TabsContent>

        {isFinanceView ? (
          <>
            <TabsContent value="payments">
              <PaymentsTable payments={payments} isLoading={paymentsLoading} />
            </TabsContent>
            <TabsContent value="debts">
              <DebtsTable debts={debts} isLoading={debtsLoading} />
            </TabsContent>
          </>
        ) : null}
      </Tabs>
    </ModulePage>
  );
}

function InvoicesTable({
  invoices,
  isLoading,
  canPay,
  estateId,
}: {
  invoices: Invoice[];
  isLoading: boolean;
  canPay: boolean;
  estateId: string;
}) {
  const queryClient = useQueryClient();

  const payMutation = useMutation({
    mutationFn: (invoice: Invoice) =>
      api.payInvoice(invoice.id, {
        amount: invoice.balance_due,
        method: "bank_transfer",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["billing-invoices", estateId] });
      queryClient.invalidateQueries({ queryKey: ["billing-payments", estateId] });
      toast.success("Payment recorded successfully.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Invoices</CardTitle>
        <CardDescription>
          {canPay
            ? "Your service charges and outstanding balances for this estate."
            : "All estate invoices including issued, partial, and overdue items."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading invoices…</p>
        ) : invoices.length === 0 ? (
          <p className="text-sm text-muted-foreground">No invoices found.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Invoice</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Due</TableHead>
                <TableHead className="text-right">Total</TableHead>
                <TableHead className="text-right">Balance</TableHead>
                {canPay ? <TableHead className="text-right">Action</TableHead> : null}
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoices.map((invoice) => {
                const balance = parseFloat(invoice.balance_due);
                const canPayInvoice =
                  canPay &&
                  balance > 0 &&
                  ["issued", "partial", "overdue"].includes(invoice.status);

                return (
                  <TableRow key={invoice.id}>
                    <TableCell className="font-medium">{invoice.invoice_number}</TableCell>
                    <TableCell>
                      <InvoiceStatusBadge status={invoice.status} />
                    </TableCell>
                    <TableCell>{formatDate(invoice.due_date)}</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(parseFloat(invoice.total_amount), invoice.currency)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(balance, invoice.currency)}
                    </TableCell>
                    {canPay ? (
                      <TableCell className="text-right">
                        {canPayInvoice ? (
                          <Button
                            size="sm"
                            disabled={payMutation.isPending}
                            onClick={() => payMutation.mutate(invoice)}
                          >
                            Pay
                          </Button>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </TableCell>
                    ) : null}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function PaymentsTable({
  payments,
  isLoading,
}: {
  payments: Payment[];
  isLoading: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Payments</CardTitle>
        <CardDescription>Recorded payments against estate invoices.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading payments…</p>
        ) : payments.length === 0 ? (
          <p className="text-sm text-muted-foreground">No payments found.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Reference</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Paid</TableHead>
                <TableHead className="text-right">Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payments.map((payment) => (
                <TableRow key={payment.id}>
                  <TableCell className="font-medium">{payment.reference}</TableCell>
                  <TableCell>
                    <PaymentStatusBadge status={payment.status} />
                  </TableCell>
                  <TableCell className="capitalize">{payment.method.replace("_", " ")}</TableCell>
                  <TableCell>
                    {payment.paid_at ? formatDateTime(payment.paid_at) : "—"}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(parseFloat(payment.amount), payment.currency)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function DebtsTable({ debts, isLoading }: { debts: DebtRecord[]; isLoading: boolean }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Debt records</CardTitle>
        <CardDescription>Units with outstanding or overdue balances.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading debt records…</p>
        ) : debts.length === 0 ? (
          <p className="text-sm text-muted-foreground">No debt records found.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Status</TableHead>
                <TableHead>Oldest due</TableHead>
                <TableHead className="text-right">Total debt</TableHead>
                <TableHead className="text-right">Overdue</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {debts.map((debt) => (
                <TableRow key={debt.id}>
                  <TableCell>
                    <DebtStatusBadge status={debt.status} />
                  </TableCell>
                  <TableCell>
                    {debt.oldest_due_date ? formatDate(debt.oldest_due_date) : "—"}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(parseFloat(debt.total_debt))}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(parseFloat(debt.overdue_amount))}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

function InvoiceStatusBadge({ status }: { status: Invoice["status"] }) {
  const variant =
    status === "paid"
      ? "success"
      : status === "overdue"
        ? "destructive"
        : status === "partial"
          ? "warning"
          : "secondary";
  return (
    <Badge variant={variant} className="capitalize">
      {status.replace("_", " ")}
    </Badge>
  );
}

function PaymentStatusBadge({ status }: { status: Payment["status"] }) {
  const variant =
    status === "completed"
      ? "success"
      : status === "failed"
        ? "destructive"
        : status === "processing"
          ? "warning"
          : "secondary";
  return (
    <Badge variant={variant} className="capitalize">
      {status}
    </Badge>
  );
}

function DebtStatusBadge({ status }: { status: DebtRecord["status"] }) {
  const variant =
    status === "settled"
      ? "success"
      : status === "overdue" || status === "in_collection"
        ? "destructive"
        : "secondary";
  return (
    <Badge variant={variant} className="capitalize">
      {status.replace("_", " ")}
    </Badge>
  );
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
