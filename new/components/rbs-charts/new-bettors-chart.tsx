// components/rbs-charts/new-bettors-chart.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, ResponsiveContainer, XAxis, YAxis, Line, ComposedChart } from "recharts"
import { Users, TrendingUp } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"

interface NewBettorsChartProps {
  data: PeriodData[]
}

export function NewBettorsChart({ data }: NewBettorsChartProps) {
  // Calculate cumulative bettors
  let cumulative = 0
  const dataWithCumulative = data.map((d) => {
    cumulative += d.new_bettors
    return { ...d, cumulative_bettors: cumulative }
  })

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-rbs-green/10 rounded-lg border border-rbs-green/20">
                <Users className="w-4 h-4 text-rbs-green" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">
                New Bettors Over Time
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Daily/Weekly/Monthly new user acquisition and cumulative growth.
            </CardDescription>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-muted rounded-lg">
            <TrendingUp className="w-3.5 h-3.5 text-accent-primary" />
            <span className="text-xs font-semibold text-accent-primary">+8.5%</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            new_bettors: {
              label: "New Bettors",
              color: "var(--rbs-green)",
            },
            cumulative_bettors: {
              label: "Cumulative Bettors",
              color: "var(--rbs-purple)",
            },
          }}
          className="h-[300px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={dataWithCumulative} margin={{ top: 20, right: 40, left: 30, bottom: 20 }}>
              <XAxis
                dataKey="start_date"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(248, 250, 252, 0.4)", fontSize: 11, fontWeight: 500 }}
                dy={10}
                tickFormatter={(value) =>
                  new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric" })
                }
              />
              <YAxis
                yAxisId="left"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(248, 250, 252, 0.4)", fontSize: 11, fontWeight: 500 }}
                tickFormatter={formatNumber}
                dx={-15}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(248, 250, 252, 0.4)", fontSize: 11, fontWeight: 500 }}
                tickFormatter={formatNumber}
                dx={15}
              />
              <ChartTooltip content={<ChartTooltipContent />} cursor={{ fill: "rgba(255, 255, 255, 0.02)" }} />
              <Bar yAxisId="left" dataKey="new_bettors" fill="var(--rbs-green)" radius={[4, 4, 0, 0]} maxBarSize={20} />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="cumulative_bettors"
                stroke="var(--rbs-purple)"
                strokeWidth={2}
                dot={{ fill: "var(--rbs-purple)", strokeWidth: 0, r: 3 }}
                activeDot={{ r: 5, stroke: "var(--rbs-purple)", strokeWidth: 2, fill: "var(--bg-base)" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
