// components/rbs-charts/submission-activity-chart.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, ResponsiveContainer, XAxis, YAxis, Line, ComposedChart } from "recharts"
import { TrendingUp, BarChart3 } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"

interface SubmissionActivityChartProps {
  data: PeriodData[]
}

export function SubmissionActivityChart({ data }: SubmissionActivityChartProps) {
  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group w-full overflow-hidden">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-rbs-blue/10 rounded-lg border border-rbs-blue/20">
                <BarChart3 className="w-4 h-4 text-rbs-blue" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">
                RareLink Submission Activity
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Total submissions and active bettors over time.
            </CardDescription>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-muted rounded-lg">
            <TrendingUp className="w-3.5 h-3.5 text-accent-primary" />
            <span className="text-xs font-semibold text-accent-primary">+15.2%</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            submissions: {
              label: "Submissions",
              color: "#D0FF12",
            },
            active_addresses: {
              label: "Active Bettors",
              color: "#5DD070",
            },
          }}
          className="h-[400px] w-full"
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
                dx={-40}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(248, 250, 252, 0.4)", fontSize: 11, fontWeight: 500 }}
                tickFormatter={formatNumber}
                dx={20}
                hide={true}
              />
              <ChartTooltip content={<ChartTooltipContent />} cursor={{ fill: "rgba(255, 255, 255, 0.02)" }} />
              <Bar yAxisId="left" dataKey="submissions" fill="#D0FF12" radius={[4, 4, 0, 0]} maxBarSize={20} />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="active_addresses"
                stroke="#5DD070"
                strokeWidth={2}
                dot={{ fill: "#5DD070", strokeWidth: 0, r: 3 }}
                activeDot={{ r: 5, stroke: "#5DD070", strokeWidth: 2, fill: "#04070D" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
