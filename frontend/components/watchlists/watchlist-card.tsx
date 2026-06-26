import { cn } from "@/lib/utils";
import type { Watchlist } from "@/features/watchlists/types";

interface WatchlistCardProps {
  watchlist: Watchlist;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

export function WatchlistCard({
  watchlist,
  isSelected,
  onSelect,
  onDelete,
}: WatchlistCardProps) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        "w-full text-left rounded-lg border p-3 transition-colors hover:bg-accent",
        isSelected
          ? "border-primary bg-accent/50"
          : "border-border bg-card"
      )}
    >
      <div className="flex items-center justify-between">
        <div className="min-w-0 flex-1">
          <p className="font-medium truncate">{watchlist.name}</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            {watchlist.items.length} {watchlist.items.length === 1 ? "ticker" : "tickers"}
          </p>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="ml-2 rounded-md p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
          title="Delete watchlist"
          aria-label="Delete watchlist"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 6h18" />
            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
          </svg>
        </button>
      </div>
    </button>
  );
}
