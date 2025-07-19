// components/rbs-charts/mon-jerry-volume-area.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { DollarSign, TrendingUp } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatCurrency } from "@/lib/utils"
import { CHART_COLORS } from "@/lib/chart-colors"

interface MonJerryVolumeAreaProps {
  data: PeriodData[]
  onChartClick?: () => void
  isModal?: boolean
}

export function MonJerryVolumeArea({ data, onChartClick, isModal = false }: MonJerryVolumeAreaProps) {
  const totalMonVolume = data.reduce((sum, period) => sum + period.mon_volume, 0)
  const totalJerryVolume = data.reduce((sum, period) => sum + period.jerry_volume, 0)
  const totalVolume = totalMonVolume + totalJerryVolume

  // Custom tooltip for modal mode (no ChartContainer context needed)
  const customTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface border border-border-subtle rounded-lg p-3 shadow-lg">
          <p className="text-text-secondary text-sm mb-2">
            {new Date(label).toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric',
              year: 'numeric'
            })}
          </p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-text-primary text-sm">
                {entry.dataKey === 'mon_volume' ? '$MON Volume' : '$JERRY Volume'}: {formatCurrency(entry.value)}
              </span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  const chartContent = (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 20, right: 40, left: 30, bottom: 20 }}>
        <defs>
          <linearGradient id="monVolumeGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#D0FF12" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#D0FF12" stopOpacity={0.05} />
          </linearGradient>
          <linearGradient id="jerryVolumeGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#EC305D" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#EC305D" stopOpacity={0.05} />
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
        {isModal ? (
          <ChartTooltip content={customTooltip} />
        ) : (
          <ChartTooltip content={<ChartTooltipContent formatter={(value) => formatCurrency(Number(value))} />} />
        )}
        <Area
          type="monotone"
          dataKey="jerry_volume"
          stackId="1"
          stroke="#EC305D"
          fill="url(#jerryVolumeGradient)"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="mon_volume"
          stackId="1"
          stroke="#D0FF12"
          fill="url(#monVolumeGradient)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  )

  if (isModal) {
    return chartContent;
  }

  const content = (
    <>
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <DollarSign className="w-4 h-4 text-blue-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">
                Token Volume Trends
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              $MON and $JERRY betting volume over time
            </CardDescription>
          </div>
          <div className="text-right">
            <p className="text-text-tertiary text-xs">MON/JERRY Ratio</p>
            <p className="text-text-primary text-sm font-semibold">
              {totalJerryVolume > 0 ? (totalMonVolume / totalJerryVolume).toFixed(2) : "N/A"}
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            mon_volume: {
              label: "$MON Volume",
              color: "#D0FF12",
            },
            jerry_volume: {
              label: "$JERRY Volume",
              color: "#EC305D",
            },
          }}
          className="h-[350px] w-full"
        >
          {chartContent}
        </ChartContainer>
      </CardContent>
    </>
  )

  if (onChartClick) {
    return (
      <div 
        className="cursor-pointer transition-all duration-200 group hover:scale-[1.02] hover:shadow-glow-medium relative"
        onClick={onChartClick}
      >
        <div className="absolute inset-0 bg-accent-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 rounded-lg" />
        
        <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="p-2 bg-bg-elevated/90 backdrop-blur-sm rounded-lg border border-border-subtle">
            <TrendingUp className="w-4 h-4 text-accent-primary" />
          </div>
        </div>
        
        <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group w-full overflow-hidden">
          {content}
        </Card>
      </div>
    )
  }

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group w-full overflow-hidden">
      {content}
    </Card>
  )
}
