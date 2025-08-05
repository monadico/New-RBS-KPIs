// components/rbs-charts/submission-activity-chart.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer } from "@/components/ui/chart"
import { Bar, ComposedChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend } from "recharts"
import { BarChart3, TrendingUp } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"
import { CHART_COLORS } from "@/lib/chart-colors"

interface SubmissionActivityChartProps {
  data: PeriodData[]
  onChartClick?: () => void
  isModal?: boolean
}

export function SubmissionActivityChart({ data, onChartClick, isModal = false }: SubmissionActivityChartProps) {
  // Calculate total submissions and active addresses
  const totalSubmissions = data.reduce((sum, period) => sum + period.submissions, 0)
  const totalActiveAddresses = data.reduce((sum, period) => sum + period.active_addresses, 0)
  
  // Standardized height for all charts
  const chartHeight = "h-[400px]"

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
            tickFormatter={formatNumber}
            dx={20}
            hide={true}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.cursor }} />
          <Bar 
            yAxisId="left"
            isAnimationActive={false}
            dataKey="submissions" 
            fill={CHART_COLORS.activity.submissions} 
            radius={[4, 4, 0, 0]} 
            maxBarSize={20} 
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="active_addresses"
            stroke={CHART_COLORS.activity.bettors}
            strokeWidth={3}
            isAnimationActive={false}
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
    </div>
  )

  const content = (
    <>
      {!isModal && (
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent-muted rounded-lg border border-accent-primary/20">
                <BarChart3 className="w-4 h-4 text-accent-primary" />
              </div>
              <div>
                <CardTitle className="text-lg font-bold text-text-primary tracking-tight">
                  Submission Activity
                </CardTitle>
                <CardDescription className="text-text-secondary">
                  Daily submission volume and active bettor trends over time
                </CardDescription>
              </div>
            </div>
          </div>
        </CardHeader>
      )}

      <CardContent className={isModal ? "p-0" : ""}>
        <ChartContainer
          config={{
            submissions: {
              label: "Submissions",
              color: CHART_COLORS.activity.submissions,
            },
            active_addresses: {
              label: "Active Bettors",
              color: CHART_COLORS.activity.bettors,
            },
          }}
          className={`${chartHeight} w-full`}
        >
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 20, right: 40, left: 50, bottom: isModal ? 60 : 40 }}>
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
                hide={true}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.cursor }} />
              <Bar 
                yAxisId="left" 
                dataKey="submissions" 
                fill={CHART_COLORS.activity.submissions} 
                radius={[4, 4, 0, 0]} 
                maxBarSize={20} 
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="active_addresses"
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

  // If this is for modal display, return standalone chart
  if (isModal) {
    return modalChart
  }

  // For regular display, wrap in clickable card
  if (onChartClick) {
    return (
      <div 
        className="cursor-pointer group relative"
        onClick={onChartClick}
      >
        {/* Border shine effect */}
        <div className="absolute inset-0 rounded-lg overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 transform -skew-x-12 -translate-x-full group-hover:translate-x-full" />
        </div>
        
        {/* Expand icon overlay */}
        <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="p-2 bg-bg-elevated/90 backdrop-blur-sm rounded-lg border border-border-subtle">
            <BarChart3 className="w-4 h-4 text-accent-primary" />
          </div>
        </div>
        
        <Card className="bg-surface border-border-subtle shadow-card-medium">
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-orange-500/10 rounded-lg border border-orange-500/20">
                    <BarChart3 className="w-4 h-4 text-orange-400" />
                  </div>
                  <CardTitle className="text-xl font-bold text-text-primary tracking-tight">Submission Activity</CardTitle>
                </div>
                <CardDescription className="text-text-secondary text-sm leading-relaxed">
                  Daily submission volume and active bettor trends over time.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="relative h-[420px] p-2 pb-4">
              <ChartContainer
                config={{
                  submissions: {
                    label: "Daily submission volume",
                    color: CHART_COLORS.activity.submissions,
                  },
                  active_addresses: {
                    label: "Active bettor trends",
                    color: CHART_COLORS.activity.bettors,
                  },
                }}
                className="h-full w-full"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={data} margin={{ top: 10, right: 20, left: 20, bottom: 30 }}>
                    <XAxis
                      dataKey="start_date"
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
                      textAnchor="middle"
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
                      hide={true}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.cursor }} />
                    <Legend verticalAlign="bottom" height={30} wrapperStyle={{ paddingTop: 10 }} />
                    <Bar 
                      yAxisId="left"
                      dataKey="submissions"
                      fill={CHART_COLORS.activity.submissions}
                      radius={[4, 4, 0, 0]}
                      maxBarSize={20}
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="active_addresses"
                      stroke={CHART_COLORS.activity.bettors}
                      strokeWidth={2}
                      dot={{ fill: CHART_COLORS.activity.bettors, strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, stroke: CHART_COLORS.activity.bettors, strokeWidth: 2 }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </ChartContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500/10 rounded-lg border border-orange-500/20">
                <BarChart3 className="w-4 h-4 text-orange-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">Submission Activity</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Daily submission volume and active bettor trends over time.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            submissions: {
              label: "Daily submission volume",
              color: CHART_COLORS.activity.submissions,
            },
            active_addresses: {
              label: "Active bettor trends",
              color: CHART_COLORS.activity.bettors,
            },
          }}
          className={chartHeight}
        >
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 20, right: 40, left: 50, bottom: 40 }}>
              <XAxis
                dataKey="start_date"
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
                hide={true}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.cursor }} />
              <Bar 
                yAxisId="left"
                dataKey="submissions"
                fill={CHART_COLORS.activity.submissions}
                radius={[4, 4, 0, 0]}
                maxBarSize={20}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="active_addresses"
                stroke={CHART_COLORS.activity.bettors}
                strokeWidth={2}
                dot={{ fill: CHART_COLORS.activity.bettors, strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: CHART_COLORS.activity.bettors, strokeWidth: 2 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
