"use client";

import { Bell, LogOut, Menu, Moon, Search, Sun, Settings } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef } from "react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useEstate } from "@/hooks/useEstate";
import { useTheme } from "@/hooks/useTheme";
import { getInitials } from "@/lib/utils";

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuth();
  const { currentEstate } = useEstate();
  const { toggleTheme, isDark, mounted } = useTheme();
  const router = useRouter();
  const searchRef = useRef<HTMLInputElement>(null);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const query = searchRef.current?.value.trim();
    if (!query) return;
    // Navigate to the most relevant module based on search terms
    const lower = query.toLowerCase();
    if (lower.includes("invoice") || lower.includes("bill") || lower.includes("payment")) {
      router.push("/billing");
    } else if (lower.includes("visitor") || lower.includes("pass") || lower.includes("gate")) {
      router.push("/visitors");
    } else if (lower.includes("ticket") || lower.includes("maintenance") || lower.includes("repair")) {
      router.push("/maintenance");
    } else if (lower.includes("resident") || lower.includes("owner") || lower.includes("tenant")) {
      router.push("/residents");
    } else if (lower.includes("package") || lower.includes("delivery") || lower.includes("parcel")) {
      router.push("/packages");
    } else if (lower.includes("park") || lower.includes("slot") || lower.includes("vehicle")) {
      router.push("/parking");
    } else if (lower.includes("security") || lower.includes("incident") || lower.includes("sos")) {
      router.push("/security");
    } else {
      router.push("/dashboard");
    }
  }

  return (
    <header className="sticky top-0 z-40 flex h-[var(--header-height)] items-center gap-4 border-b bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60 lg:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
        aria-label="Open navigation menu"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <form
        onSubmit={handleSearch}
        className="relative hidden max-w-md flex-1 md:block"
      >
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          ref={searchRef}
          placeholder="Search residents, tickets, invoices..."
          className="pl-9"
          aria-label="Search"
        />
      </form>

      <div className="ml-auto flex items-center gap-2">
        {currentEstate && (
          <div className="hidden rounded-lg border px-3 py-1.5 text-sm sm:block">
            <span className="text-muted-foreground">Estate: </span>
            <span className="font-medium">{currentEstate.name}</span>
          </div>
        )}

        <Button
          variant="ghost"
          size="icon"
          aria-label="Notifications"
          asChild
        >
          <Link href="/settings?tab=notifications">
            <Bell className="h-5 w-5" />
          </Link>
        </Button>

        {mounted && (
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
        )}

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-9 w-9 rounded-full">
              <Avatar className="h-9 w-9">
                <AvatarImage src={user?.avatar ?? undefined} alt="" />
                <AvatarFallback>
                  {getInitials(user?.first_name, user?.last_name)}
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <Link href="/settings">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="text-destructive">
              <LogOut className="mr-2 h-4 w-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
