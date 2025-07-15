// components/rbs-charts/total-avg-cards-chart.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, ResponsiveContainer, XAxis, YAxis, Line, ComposedChart } from "recharts"
import { CreditCard } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"

interface TotalAvgCardsChartProps {
  data: PeriodData[]
}

export function TotalAvgCardsChart({ data }: TotalAvgCardsChartProps) {
  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group lg:col-span-full">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500/10 rounded-lg border border-orange-500/20">
                <CreditCard className="w-4 h-4 text-orange-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">
                Total & Average Cards Over Time
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Total cards submitted and average cards per RareLink submission.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            total_cards: {
              label: "Total Cards",
              color: "var(--rbs-blue)",
            },
            avg_cards_per_submission: {
              label: "Avg Cards/Submission",
              color: "var(--rbs-orange)",
            },
          }}
          className="h-[350px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 20, right: 40, left: 30, bottom: 20 }}>
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
                tickFormatter={(value: number) => value.toFixed(1)}
                dx={15}
              />
              <ChartTooltip content={<ChartTooltipContent />} cursor={{ fill: "rgba(255, 255, 255, 0.02)" }} />
              <Bar yAxisId="left" dataKey="total_cards" fill="var(--rbs-blue)" radius={[4, 4, 0, 0]} maxBarSize={20} />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="avg_cards_per_submission"
                stroke="var(--rbs-orange)"
                strokeWidth={2}
                dot={{ fill: "var(--rbs-orange)", strokeWidth: 0, r: 3 }}
                activeDot={{ r: 5, stroke: "var(--rbs-orange)", strokeWidth: 2, fill: "var(--bg-base)" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
