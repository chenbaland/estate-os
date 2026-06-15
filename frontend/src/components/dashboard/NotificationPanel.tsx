"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCircle2, Info, AlertTriangle, Check } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "@/components/ui/toast";
import { api } from "@/lib/api";
import { formatRelativeTime } from "@/lib/utils";
import type { Notification } from "@/types";

function notifIcon(notif: Notification) {
  if (notif.status === "read") return CheckCircle2;
  if (notif.priority === "critical" || notif.priority === "high") return AlertTriangle;
  return Info;
}

function notifColor(notif: Notification) {
  if (notif.status === "read") return "text-muted-foreground";
  if (notif.priority === "critical") return "text-destructive";
  if (notif.priority === "high") return "text-warning";
  return "text-info";
}

export function NotificationPanel() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["notifications-panel"],
    queryFn: () => api.getNotifications(),
    refetchInterval: 30_000,
  });

  const notifications = data?.results ?? [];
  const unreadCount = notifications.filter((n) => n.status !== "read").length;

  const markAllMutation = useMutation({
    mutationFn: () => api.markAllNotificationsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications-panel"] });
      toast.success("All notifications marked as read.");
    },
  });

  const markOneMutation = useMutation({
    mutationFn: (id: string) => api.markNotificationRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications-panel"] });
    },
  });

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">Notifications</CardTitle>
        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <>
              <Badge variant="secondary">{unreadCount} new</Badge>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs"
                disabled={markAllMutation.isPending}
                onClick={() => markAllMutation.mutate()}
              >
                <Check className="mr-1 h-3 w-3" />
                Mark all read
              </Button>
            </>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[320px]">
          {isLoading ? (
            <div className="space-y-3 px-6 py-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex gap-3">
                  <Skeleton className="h-4 w-4 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-3 w-3/4" />
                    <Skeleton className="h-3 w-full" />
                  </div>
                </div>
              ))}
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Bell className="h-8 w-8 text-muted-foreground/40" />
              <p className="mt-2 text-sm text-muted-foreground">No notifications yet</p>
            </div>
          ) : (
            <ul className="divide-y">
              {notifications.slice(0, 8).map((notification) => {
                const Icon = notifIcon(notification);
                const isUnread = notification.status !== "read";
                return (
                  <li
                    key={notification.id}
                    className={`flex gap-3 px-6 py-4 ${isUnread ? "bg-accent/30" : ""}`}
                  >
                    <div className={`mt-0.5 ${notifColor(notification)}`}>
                      <Icon className="h-4 w-4" aria-hidden />
                    </div>
                    <div className="min-w-0 flex-1 space-y-1">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-medium leading-none">
                          {notification.title}
                        </p>
                        <div className="flex items-center gap-1 shrink-0">
                          {isUnread && (
                            <>
                              <span className="h-2 w-2 rounded-full bg-primary" />
                              <button
                                type="button"
                                aria-label="Mark as read"
                                className="text-muted-foreground hover:text-foreground"
                                onClick={() => markOneMutation.mutate(notification.id)}
                              >
                                <Check className="h-3 w-3" />
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {notification.body}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatRelativeTime(notification.created_at)}
                      </p>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </ScrollArea>
        <div className="border-t p-4">
          <Link
            href="/settings"
            className="flex w-full items-center justify-center gap-2 text-sm text-muted-foreground hover:text-foreground"
          >
            <Bell className="h-4 w-4" />
            Notification preferences
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
