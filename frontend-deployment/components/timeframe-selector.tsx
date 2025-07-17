// components/timeframe-selector.tsx
"use client"

import { Button } from "@/components/ui/button"
import { cn } from "../lib/utils"

interface TimeframeSelectorProps {
  selectedTimeframe: "daily" | "weekly" | "monthly"
  onSelectTimeframe: (timeframe: "daily" | "weekly" | "monthly") => void
}

export function TimeframeSelector({ selectedTimeframe, onSelectTimeframe }: TimeframeSelectorProps) {
  const buttonClass = (timeframe: string) =>
    cn(
      "px-6 py-3 rounded-full text-sm font-medium transition-all duration-300",
      selectedTimeframe === timeframe
        ? "bg-rbs-lime text-rbs-black shadow-glow-subtle"
        : "bg-surface-elevated text-text-secondary hover:bg-surface hover:text-text-primary border border-border-subtle",
    )

  return (
    <div className="flex justify-center gap-4 mb-8 animate-fade-in-up">
      <Button className={buttonClass("daily")} onClick={() => onSelectTimeframe("daily")}>
        Daily
      </Button>
      <Button className={buttonClass("weekly")} onClick={() => onSelectTimeframe("weekly")}>
        Weekly
      </Button>
      <Button className={buttonClass("monthly")} onClick={() => onSelectTimeframe("monthly")}>
        Monthly
      </Button>
    </div>
  )
}
