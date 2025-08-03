// components/rbs-charts/total-avg-cards-chart.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, ComposedChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"
import { Layers, TrendingUp } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"
import { CHART_COLORS } from "@/lib/chart-colors"

interface TotalAvgCardsChartProps {
  data: PeriodData[]
  onChartClick?: () => void
  isModal?: boolean
}

export function TotalAvgCardsChart({ data, onChartClick, isModal = false }: TotalAvgCardsChartProps) {
  // Calculate totals
  const totalCards = data.reduce((sum, period) => sum + period.total_cards, 0)
  const avgCardsPerSubmission = data.reduce((sum, period) => sum + period.avg_cards_per_submission, 0) / data.length

  // Use smaller height for modal to ensure it fits within bounds and shows X-axis
  const chartHeight = isModal ? "h-[450px]" : "h-[515px]"

  // Custom tooltip for modal chart
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-surface border border-border-subtle rounded-lg p-3 shadow-lg">
          <p className="text-text-secondary text-sm mb-2">
            {(() => {
              const [year, month, day] = label.split('-').map(Number)
              const date = new Date(year, month - 1, day)
              return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                year: 'numeric'
              })
            })()}
          </p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-text-primary text-sm">
                {entry.name}: {entry.name.includes('Average') 
                  ? entry.value.toFixed(2) 
                  : formatNumber(entry.value)
                }
              </span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  // Create standalone chart for modal mode
  const modalChart = (
    <div className="w-full h-[450px]">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 20, right: 40, left: 50, bottom: isModal ? 60 : 40 }}>
          <XAxis
            dataKey="start_date"
            dy={isModal ? 10 : 0}
            tickLine={false}
            axisLine={false}
            tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
            tickFormatter={(value) => {
              // Parse date as local time to avoid timezone issues
              const [year, month, day] = value.split('-').map(Number)
              const date = new Date(year, month - 1, day) // month is 0-indexed
              return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric' 
              })
            }}
          />
          <YAxis
            yAxisId="left"
            axisLine={false}
            tickLine={false}
            tick={{ fill: CHART_COLORS.axis.text, fontSize: 11, fontWeight: 500 }}
            tickFormatter={formatNumber}
            dx={-40}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            axisLine={false}
            tickLine={false}
            tick={{ fill: CHART_COLORS.axis.text, fontSize: 11, fontWeight: 500 }}
            tickFormatter={(value) => value.toFixed(1)}
            dx={20}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.cursor }} />
          <Bar 
            yAxisId="left" 
            dataKey="total_cards" 
            fill={CHART_COLORS.cards.total} 
            radius={[4, 4, 0, 0]} 
            maxBarSize={20}
            name="Total Cards"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="avg_cards_per_submission"
            stroke={CHART_COLORS.cards.average}
            strokeWidth={3}
            dot={{ fill: CHART_COLORS.cards.average, strokeWidth: 0, r: 4 }}
            activeDot={{ 
              r: 6, 
              stroke: CHART_COLORS.cards.average, 
              strokeWidth: 2, 
              fill: CHART_COLORS.activeDot.stroke,
              filter: `drop-shadow(${CHART_COLORS.activeDot.glow})`
            }}
            name="Average Cards"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )

  // If this is for modal display, return standalone chart
  if (isModal) {
    return modalChart
  }

  const content = (
    <Card className="bg-surface border-border-subtle shadow-card-medium transition-all duration-500 group flex flex-col h-full">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500/10 rounded-lg border border-orange-500/20">
                <TrendingUp className="w-4 h-4 text-orange-400" />
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
      <CardContent className="flex-grow">
        <ChartContainer
          config={{
            total_cards: {
              label: "Total Cards",
              color: "#D0FF12",
            },
            avg_cards_per_submission: {
              label: "Avg Cards/Submission",
              color: "#1E90FF",
            },
          }}
          className="h-full w-full"
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
                  new Date(value + 'T00:00:00').toLocaleDateString("en-US", { month: "short", day: "numeric" })
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
              <Bar yAxisId="left" dataKey="total_cards" fill="#D0FF12" radius={[4, 4, 0, 0]} maxBarSize={20} />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="avg_cards_per_submission"
                stroke="#1E90FF"
                strokeWidth={2}
                dot={{ fill: "#1E90FF", strokeWidth: 0, r: 3 }}
                activeDot={{ r: 5, stroke: "#1E90FF", strokeWidth: 2, fill: "var(--bg-base)" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )

  // If click handler provided, make it clickable
  if (onChartClick) {
    return (
      <div 
        className="cursor-pointer transition-all duration-200 group relative"
        onClick={onChartClick}
      >
        {/* Expand icon overlay */}
        <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="p-2 bg-bg-elevated/90 backdrop-blur-sm rounded-lg border border-border-subtle">
            <Layers className="w-4 h-4 text-accent-primary" />
          </div>
        </div>
        
        {content}
      </div>
    )
  }

  return content
}
