"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  LayoutDashboard,
  ListChecks,
  TrendingUp,
  BarChart3,
  Signal,
  PieChart,
  Bell,
  Settings,
  ChevronLeft,
} from "lucide-react";
import { useUnreadCountQuery } from "@/features/notifications/hooks";

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
  { label: "Portfolio", href: "/dashboard/portfolio", icon: <PieChart className="h-4 w-4" /> },
  { label: "Alerts", href: "/dashboard/alerts", icon: <Bell className="h-4 w-4" /> },
  { label: "Settings", href: "/dashboard/settings", icon: <Settings className="h-4 w-4" /> },
];

interface AppSidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

export function AppSidebar({ collapsed = false, onToggle }: AppSidebarProps) {
  const pathname = usePathname();
  const { data: unreadCount } = useUnreadCountQuery();
  const alertBadge = unreadCount?.count ?? 0;

  return (
    <aside
      className={cn(
        "flex flex-col border-r bg-card transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-14 items-center justify-between px-4">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
            <Signal className="h-5 w-5 text-primary" />
            <span>Insique</span>
          </Link>
        )}
        {collapsed && (
          <Link href="/dashboard" className="mx-auto">
            <Signal className="h-5 w-5 text-primary" />
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={cn(collapsed && "mx-auto")}
        >
          <ChevronLeft className={cn("h-4 w-4 transition-transform", collapsed && "rotate-180")} />
        </Button>
      </div>

      <Separator />

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => (
          <Button
            key={item.href}
            variant={pathname === item.href ? "secondary" : "ghost"}
            className={cn(
              "w-full justify-start",
              collapsed ? "justify-center px-2" : "px-3",
              item.disabled && "opacity-50 cursor-not-allowed"
            )}
            asChild={!item.disabled}
            disabled={item.disabled}
          >
            {item.disabled ? (
              <span className="flex items-center gap-3">
                {item.icon}
                {!collapsed && <span>{item.label}</span>}
              </span>
            ) : (
              <Link href={item.href} className="flex items-center gap-3">
                {item.href === "/dashboard/alerts" && alertBadge > 0 ? (
                  <div className="relative">
                    {item.icon}
                    <Badge
                      variant="destructive"
                      className="absolute -right-2 -top-2 flex h-4 min-w-[16px] items-center justify-center rounded-full px-1 text-[9px]"
                    >
                      {alertBadge > 99 ? "99+" : alertBadge}
                    </Badge>
                  </div>
                ) : (
                  item.icon
                )}
                {!collapsed && (
                  <span>{item.label}</span>
                )}
                {!collapsed && item.href === "/dashboard/alerts" && alertBadge > 0 && (
                  <Badge
                    variant="secondary"
                    className="ml-auto h-5 px-1.5 text-[10px]"
                  >
                    {alertBadge > 99 ? "99+" : alertBadge}
                  </Badge>
                )}
              </Link>
            )}
          </Button>
        ))}
      </nav>
    </aside>
  );
}
