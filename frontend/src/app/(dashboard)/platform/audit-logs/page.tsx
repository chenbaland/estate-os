"use client";

import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";

const ACTION_LABELS: Record<string, string> = {
  "estate.created": "Estate created",
  "estate.updated": "Estate updated",
  "estate.deactivated": "Estate deactivated",
  "estate.activated": "Estate activated",
  "admin.assigned": "Admin assigned",
  "admin.revoked": "Admin revoked",
};

function formatAction(action: string) {
  return ACTION_LABELS[action] ?? action;
}

function formatTimestamp(value: string) {
  return new Date(value).toLocaleString();
}

export default function PlatformAuditLogsPage() {
  const { data: logs = [], isLoading } = useQuery({
    queryKey: ["platform-audit-logs"],
    queryFn: async () => {
      const response = await api.getPlatformAuditLogs();
      return response.results;
    },
  });

  return (
    <div className="space-y-6">
      <p className="text-muted-foreground">
        Immutable record of super-admin actions across the platform.
      </p>

      <Card>
        <CardHeader>
          <CardTitle>Audit logs</CardTitle>
          <CardDescription>
            Estate provisioning, admin assignments, and activation changes
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Loading audit logs...</p>
          ) : logs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No audit events recorded yet.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>When</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Summary</TableHead>
                  <TableHead>Actor</TableHead>
                  <TableHead>Estate</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="whitespace-nowrap text-sm">
                      {formatTimestamp(log.created_at)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{formatAction(log.action)}</Badge>
                    </TableCell>
                    <TableCell>{log.summary}</TableCell>
                    <TableCell>
                      {log.actor_name ?? log.actor_email ?? "System"}
                    </TableCell>
                    <TableCell>{log.estate_name ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
