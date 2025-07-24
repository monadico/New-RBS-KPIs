// components/rbs-charts/new-bettors-chart.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, ComposedChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"
import { Users, TrendingUp } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"
import { CHART_COLORS } from "@/lib/chart-colors"

interface NewBettorsChartProps {
  data: PeriodData[]
  onChartClick?: () => void
  isModal?: boolean
}

export function NewBettorsChart({ data, onChartClick, isModal = false }: NewBettorsChartProps) {
  // Calculate cumulative bettors for the line
  let cumulativeBettors = 1000 // Starting point
  const dataWithCumulative = data.map((period) => {
    cumulativeBettors += period.new_bettors
    return {
      ...period,
      cumulative_bettors: cumulativeBettors,
    }
  })

  // Calculate totals
  const totalNewBettors = data.reduce((sum, period) => sum + period.new_bettors, 0)
  const finalCumulative = cumulativeBettors
  
  // Use smaller height for modal to ensure it fits within bounds and shows X-axis
  const chartHeight = isModal ? "h-[450px]" : "h-[400px]"

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
                {entry.name}: {formatNumber(entry.value)}
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
        <ComposedChart data={dataWithCumulative} margin={{ top: 20, right: 40, left: 50, bottom: isModal ? 60 : 40 }}>
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
            tickFormatter={formatNumber}
            dx={20}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.cursor }} />
          <Bar 
            yAxisId="left" 
            dataKey="new_bettors" 
            fill={CHART_COLORS.activity.newBettors} 
            radius={[4, 4, 0, 0]} 
            maxBarSize={20} 
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="cumulative_bettors"
            stroke={CHART_COLORS.secondary}
            strokeWidth={3}
            dot={{ fill: CHART_COLORS.secondary, strokeWidth: 0, r: 4 }}
            activeDot={{ 
              r: 6, 
              stroke: CHART_COLORS.secondary, 
              strokeWidth: 2, 
              fill: CHART_COLORS.activeDot.stroke,
              filter: `drop-shadow(${CHART_COLORS.activeDot.glow})`
            }}
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
    <>
      {!isModal && (
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent-muted rounded-lg border border-accent-primary/20">
                <Users className="w-4 h-4 text-accent-primary" />
              </div>
              <div>
                <CardTitle className="text-lg font-bold text-text-primary tracking-tight">
                  New Bettors Growth
                </CardTitle>
                <CardDescription className="text-text-secondary">
                  New and cumulative bettor acquisition over time
                </CardDescription>
              </div>
            </div>
          </div>
        </CardHeader>
      )}

      <CardContent className={isModal ? "p-0" : ""}>
        <ChartContainer
          config={{
            new_bettors: {
              label: "New Bettors",
              color: CHART_COLORS.activity.newBettors,
            },
            cumulative_bettors: {
              label: "Cumulative Bettors",
              color: CHART_COLORS.activity.bettors,
            },
          }}
          className={`${chartHeight} w-full`}
        >
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={dataWithCumulative} margin={{ top: 20, right: 40, left: 50, bottom: isModal ? 60 : 40 }}>
              <XAxis
                dataKey="start_date"
                dy={isModal ? 10 : 0}
                tickLine={false}
                axisLine={false}
                tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                tickFormatter={(value) => {
                  // Ensure date is parsed as local date, not UTC
                  const date = new Date(value + 'T00:00:00')
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
                dx={-15}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                axisLine={false}
                tickLine={false}
                tick={{ fill: CHART_COLORS.axis.text, fontSize: 11, fontWeight: 500 }}
                tickFormatter={formatNumber}
                dx={15}
                hide={true}
              />
              <Tooltip content={<ChartTooltipContent />} cursor={{ fill: CHART_COLORS.cursor }} />
              <Bar 
                yAxisId="left" 
                dataKey="new_bettors" 
                fill={CHART_COLORS.activity.newBettors} 
                radius={[4, 4, 0, 0]} 
                maxBarSize={20} 
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="cumulative_bettors"
                stroke={CHART_COLORS.activity.bettors}
                strokeWidth={3}
                dot={{ fill: CHART_COLORS.activity.bettors, strokeWidth: 0, r: 4 }}
                activeDot={{ 
                  r: 6, 
                  stroke: CHART_COLORS.activity.bettors, 
                  strokeWidth: 2, 
                  fill: CHART_COLORS.activeDot.stroke,
                  filter: `drop-shadow(${CHART_COLORS.activeDot.glow})`
                }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </>
  )

  // For regular display, wrap in clickable card
  if (onChartClick) {
    return (
      <div 
        className="cursor-pointer transition-all duration-200 group hover:scale-[1.02] hover:shadow-glow-medium relative"
        onClick={onChartClick}
      >
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-accent-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 rounded-lg" />
        
        {/* Expand icon overlay */}
        <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="p-2 bg-bg-elevated/90 backdrop-blur-sm rounded-lg border border-border-subtle">
            <Users className="w-4 h-4 text-accent-primary" />
          </div>
        </div>
        
        <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500">
          {content}
        </Card>
      </div>
    )
  }

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500">
      {content}
    </Card>
  )
}
