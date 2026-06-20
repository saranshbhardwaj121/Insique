"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { Moon, Sun, User as UserIcon, LogOut, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MobileNav } from "@/components/app/mobile-nav";
import { useAuth } from "@/features/auth/context";
import { useTickerContext } from "@/features/ticker/ticker-context";

export function TopBar() {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const { recentTickers, setActiveTicker } = useTickerContext();
  const router = useRouter();
  const [mounted, setMounted] = React.useState(false);
  const [searchFocused, setSearchFocused] = React.useState(false);
  const [searchInput, setSearchInput] = React.useState("");
  const searchRef = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "/" && !e.ctrlKey && !e.metaKey && document.activeElement !== searchRef.current) {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const ticker = searchInput.trim().toUpperCase();
    if (ticker) {
      setActiveTicker(ticker);
      setSearchInput("");
      setSearchFocused(false);
      router.push(`/dashboard/analytics?ticker=${encodeURIComponent(ticker)}`);
    }
  };

  const handleRecentClick = (ticker: string) => {
    setActiveTicker(ticker);
    setSearchInput("");
    setSearchFocused(false);
    router.push(`/dashboard/analytics?ticker=${encodeURIComponent(ticker)}`);
  };

  const initials = user?.username
    ? user.username.slice(0, 2).toUpperCase()
    : "SF";

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-card px-4 lg:px-6">
      <MobileNav />

      <form onSubmit={handleSearchSubmit} className="relative hidden sm:block flex-1 max-w-xs">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground pointer-events-none" />
        <Input
          ref={searchRef}
          placeholder="Search ticker... (/)"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          onFocus={() => setSearchFocused(true)}
          onBlur={() => setTimeout(() => setSearchFocused(false), 200)}
          className="pl-8 h-8 text-sm"
        />
        {searchFocused && recentTickers.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 rounded-md border bg-popover shadow-md z-50">
            <p className="px-3 py-1.5 text-xs font-medium text-muted-foreground">
              Recent tickers
            </p>
            {recentTickers.slice(0, 5).map((rt) => (
              <button
                key={rt.ticker}
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  handleRecentClick(rt.ticker);
                }}
                className="w-full text-left px-3 py-1.5 text-sm hover:bg-accent transition-colors flex items-center gap-2"
              >
                <Search className="h-3 w-3 text-muted-foreground" />
                <span className="font-medium">{rt.ticker}</span>
              </button>
            ))}
          </div>
        )}
      </form>

      <div className="flex-1 sm:flex-none" />

      {mounted && (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
          <span className="sr-only">Toggle theme</span>
        </Button>
      )}

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="rounded-full">
            <Avatar className="h-8 w-8">
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium leading-none">{user?.username}</p>
              <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => logout()}>
            <LogOut className="mr-2 h-4 w-4" />
            <span>Log out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
