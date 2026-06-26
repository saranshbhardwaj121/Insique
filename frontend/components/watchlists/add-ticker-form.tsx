"use client";

import { TickerSearchForm } from "@/components/shared/ticker-search-form";
import { useAddTickerMutation } from "@/features/watchlists/hooks";

interface AddTickerFormProps {
  watchlistId: string;
}

export function AddTickerForm({ watchlistId }: AddTickerFormProps) {
  const addTickerMutation = useAddTickerMutation();

  return (
    <TickerSearchForm
      onSubmit={(ticker) => addTickerMutation.mutate({ watchlistId, ticker })}
      placeholder="Search and add ticker..."
      buttonLabel="Add"
      className="w-full max-w-none"
    />
  );
}
