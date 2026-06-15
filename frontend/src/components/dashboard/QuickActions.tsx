"use client";

import Link from "next/link";
import {
  Bot,
  CreditCard,
  Package,
  Shield,
  UserPlus,
  Wrench,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const actions = [
  {
    title: "Register Visitor",
    href: "/visitors",
    icon: UserPlus,
    description: "Issue a new visitor pass",
  },
  {
    title: "Report Issue",
    href: "/maintenance",
    icon: Wrench,
    description: "Submit maintenance ticket",
  },
  {
    title: "Pay Bill",
    href: "/billing",
    icon: CreditCard,
    description: "View and pay invoices",
  },
  {
    title: "Track Package",
    href: "/packages",
    icon: Package,
    description: "Check delivery status",
  },
  {
    title: "Security Alert",
    href: "/security",
    icon: Shield,
    description: "Report incident or SOS",
  },
  {
    title: "Ask Concierge",
    href: "/ai-concierge",
    icon: Bot,
    description: "Get AI assistance",
  },
];

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {actions.map((action) => {
            const Icon = action.icon;
            return (
              <Button
                key={action.href}
                variant="outline"
                className="h-auto justify-start gap-3 px-4 py-3"
                asChild
              >
                <Link href={action.href}>
                  <div className="rounded-md bg-primary/10 p-2 text-primary">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium">{action.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {action.description}
                    </p>
                  </div>
                </Link>
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
