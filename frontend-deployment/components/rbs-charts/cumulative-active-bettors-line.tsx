// components/rbs-charts/cumulative-active-bettors-line.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Line, LineChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { Users } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"

interface CumulativeActiveBettorsLineProps {
  data: PeriodData[]
}

export function CumulativeActiveBettorsLine({ data }: CumulativeActiveBettorsLineProps) {
  // Calculate cumulative active bettors
  let cumulative = 0
  const dataWithCumulative = data.map((d) => {
    cumulative += d.active_addresses // Assuming active_addresses can be summed for cumulative
    return { ...d, cumulative_active_bettors: cumulative }
  })

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group lg:col-span-full">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
                <Users className="w-4 h-4 text-purple-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">
                Cumulative Active Bettors
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Total unique active bettors over time.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            cumulative_active_bettors: {
              label: "Cumulative Active Bettors",
              color: "#8F65F7",
            },
          }}
          className="h-[350px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={dataWithCumulative} margin={{ top: 20, right: 40, left: 30, bottom: 20 }}>
              <XAxis
                dataKey="start_date"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(248, 250, 252, 0.4)", fontSize: 11, fontWeight: 500 }}
                dy={10}
                tickFormatter={(value) => {
                  const [year, month, day] = value.split('-').map(Number)
                  const date = new Date(year, month - 1, day)
                  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
                }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(248, 250, 252, 0.4)", fontSize: 11, fontWeight: 500 }}
                tickFormatter={formatNumber}
                dx={-15}
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line
                type="monotone"
                dataKey="cumulative_active_bettors"
                stroke="#8F65F7"
                strokeWidth={3}
                dot={{ fill: "#8F65F7", strokeWidth: 0, r: 4 }}
                activeDot={{ r: 6, stroke: "#8F65F7", strokeWidth: 2, fill: "var(--bg-base)" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
