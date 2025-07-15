// components/metric-card.tsx
import { Card, CardContent } from "@/components/ui/card"
import { TrendingUp, TrendingDown } from "lucide-react"
import { cn, formatNumber, formatCurrency } from "@/lib/utils" // Import utility functions
import type React from "react"

interface MetricCardProps {
  title: string
  value: number
  format: "number" | "currency" | "decimal"
  change?: number
  icon?: React.ReactNode
  trend?: "up" | "down"
  subtitle?: string
  accentColor?: string // New prop for accent color
}

export function MetricCard({
  title,
  value,
  format,
  change,
  icon,
  trend,
  subtitle,
  accentColor = "text-rbs-blue",
}: MetricCardProps) {
  const formattedValue =
    format === "currency" ? formatCurrency(value) : format === "number" ? formatNumber(value) : value.toFixed(1)

  return (
    <Card className="group relative bg-surface border-border-subtle shadow-card-subtle hover:shadow-card-medium hover:bg-surface-elevated transition-all duration-500 ease-out overflow-hidden">
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-accent-muted opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      {/* Shimmer effect on hover */}
      <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out">
        <div className="h-full w-1/3 bg-gradient-to-r from-transparent via-white/5 to-transparent skew-x-12" />
      </div>

      <CardContent className="relative p-6">
        {/* Header with asymmetrical layout */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <p className="text-text-secondary text-sm font-medium tracking-wide mb-1">{title}</p>
            {subtitle && <p className="text-text-tertiary text-xs">{subtitle}</p>}
          </div>
          {icon && (
            <div className="p-2.5 bg-bg-elevated rounded-xl border border-border-subtle group-hover:border-accent-muted transition-colors duration-300">
              <div className="text-text-secondary group-hover:text-accent-primary transition-colors duration-300">
                {icon}
              </div>
            </div>
          )}
        </div>

        {/* Value with enhanced typography */}
        <div className="mb-3">
          <div
            className={cn(
              "text-5xl font-bold tracking-tight mb-1 group-hover:text-accent-primary transition-colors duration-300",
              accentColor,
            )}
          >
            {formattedValue}
          </div>
        </div>

        {/* Trend indicator with micro-interaction */}
        {change !== undefined && trend && (
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold transition-all duration-300",
                trend === "up"
                  ? "bg-green-500/10 text-green-400 border border-green-500/20"
                  : "bg-red-500/10 text-red-400 border border-red-500/20",
              )}
            >
              {trend === "up" ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              <span>{Math.abs(change)}%</span>
            </div>
            <span className="text-text-tertiary text-xs">vs last period</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
