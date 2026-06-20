"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  ListChecks,
  TrendingUp,
  BarChart3,
  Signal,
  Settings,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  disabled?: boolean;
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },
  { label: "Watchlists", href: "/dashboard/watchlists", icon: <ListChecks className="h-4 w-4" /> },
  { label: "Market Data", href: "/dashboard/market-data", icon: <TrendingUp className="h-4 w-4" /> },
  { label: "Analytics", href: "/dashboard/analytics", icon: <BarChart3 className="h-4 w-4" /> },
  { label: "Signals", href: "/dashboard/signals", icon: <Signal className="h-4 w-4" /> },
  { label: "Settings", href: "/dashboard/settings", icon: <Settings className="h-4 w-4" /> },
];

export function MobileNav() {
  const pathname = usePathname();
  const [open, setOpen] = React.useState(false);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle navigation menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-64 p-0">
        <div className="flex h-14 items-center px-4">
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold" onClick={() => setOpen(false)}>
            <Signal className="h-5 w-5 text-primary" />
            <span>Insique</span>
          </Link>
        </div>
        <Separator />
        <nav className="space-y-1 p-2">
          {navItems.map((item) => (
            <Button
              key={item.href}
              variant={pathname === item.href ? "secondary" : "ghost"}
              className={cn("w-full justify-start px-3", item.disabled && "opacity-50 cursor-not-allowed")}
              disabled={item.disabled}
              asChild={!item.disabled}
              onClick={() => !item.disabled && setOpen(false)}
            >
              {item.disabled ? (
                <span className="flex items-center gap-3">
                  {item.icon}
                  <span>{item.label}</span>
                </span>
              ) : (
                <Link href={item.href} className="flex items-center gap-3">
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              )}
            </Button>
          ))}
        </nav>
      </SheetContent>
    </Sheet>
  );
}
