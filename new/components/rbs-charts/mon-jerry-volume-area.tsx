// components/rbs-charts/mon-jerry-volume-area.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { DollarSign } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatCurrency } from "@/lib/utils"

interface MonJerryVolumeAreaProps {
  data: PeriodData[]
}

export function MonJerryVolumeArea({ data }: MonJerryVolumeAreaProps) {
  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group lg:col-span-full">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <DollarSign className="w-4 h-4 text-blue-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">
                $MON & $JERRY Volume Deposited
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Total volume of $MON and $JERRY deposited in RareLinks over time.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            mon_volume: {
              label: "$MON Volume",
              color: "var(--rbs-blue)",
            },
            jerry_volume: {
              label: "$JERRY Volume",
              color: "var(--rbs-green)",
            },
          }}
          className="h-[350px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 20, right: 40, left: 30, bottom: 20 }}>
              <defs>
                <linearGradient id="monVolumeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--rbs-blue)" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="var(--rbs-blue)" stopOpacity={0.05} />
                </linearGradient>
                <linearGradient id="jerryVolumeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--rbs-green)" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="var(--rbs-green)" stopOpacity={0.05} />
                </linearGradient>
              </defs>
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
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(248, 250, 252, 0.4)", fontSize: 11, fontWeight: 500 }}
                tickFormatter={formatCurrency}
                dx={-15}
              />
              <ChartTooltip content={<ChartTooltipContent formatter={(value: number) => formatCurrency(value)} />} />
              <Area
                type="monotone"
                dataKey="jerry_volume"
                stackId="1"
                stroke="var(--rbs-green)"
                fill="url(#jerryVolumeGradient)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="mon_volume"
                stackId="1"
                stroke="var(--rbs-blue)"
                fill="url(#monVolumeGradient)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
