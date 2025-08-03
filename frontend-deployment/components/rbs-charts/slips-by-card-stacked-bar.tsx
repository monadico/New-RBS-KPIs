// components/rbs-charts/slips-by-card-stacked-bar.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend } from "recharts"
import { CreditCard, TrendingUp } from "lucide-react"
import type { TimeframeCardCounts } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"
import { CHART_COLORS } from "@/lib/chart-colors"
import { ChartContainer } from "@/components/ui/chart"

const CARD_COUNTS = [2, 3, 4, 5, 6, 7]

interface SlipsByCardStackedBarProps {
  data: TimeframeCardCounts[]
  onChartClick?: () => void
  isModal?: boolean
}

export function SlipsByCardStackedBar({ data, onChartClick, isModal = false }: SlipsByCardStackedBarProps) {
  // Transform data to include all card counts with default 0 values
  const transformedData = data.map((period) => {
    const transformed: any = {
      period: period.period_start,
      total: 0,
    }

    // Initialize all card counts to 0
    CARD_COUNTS.forEach((count) => {
      transformed[`${count}cards`] = 0
    })

    // Fill in actual data - card_counts is a number array where index corresponds to card count
    period.card_counts.forEach((bets, index) => {
      if (bets > 0) {
        const cardCount = index + 2 // card counts start from 2
        const key = `${cardCount}cards`
        transformed[key] = bets
        transformed.total += bets
      }
    })

    return transformed
  })

  // Calculate totals for all card counts
  const totalBets = transformedData.reduce((sum, period) => sum + period.total, 0)

  // Chart config for ChartContainer
  const chartConfig = {
    cards: {
      label: "Cards",
      color: "#2563eb",
    },
  }

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
          {payload.filter((entry: any) => entry.value > 0).map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-text-primary text-sm">
                {entry.dataKey.replace('cards', ' cards')}: {formatNumber(entry.value)}
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
        <BarChart
          data={transformedData}
          margin={{ top: 20, right: 40, left: 50, bottom: isModal ? 60 : 40 }}
        >
          <XAxis
            dataKey="period"
            dy={isModal ? 10 : 0}
            axisLine={false}
            tickLine={false}
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
            axisLine={false}
            tickLine={false}
            tick={{ fill: CHART_COLORS.axis.text, fontSize: 11, fontWeight: 500 }}
            tickFormatter={formatNumber}
            dx={-30}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: CHART_COLORS.cursor }} />
          <Legend />
          {CARD_COUNTS.map((count, index) => (
            <Bar
              key={count}
              dataKey={`${count}cards`}
              stackId="cards"
              fill={CHART_COLORS.extended[index % CHART_COLORS.extended.length]}
              name={`${count} card${count > 1 ? 's' : ''}`}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )

  // If this is for modal display, return standalone chart
  if (isModal) {
    return modalChart
  }

  const content = (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 flex flex-col h-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-accent-muted rounded-lg border border-accent-primary/20">
              <CreditCard className="w-4 h-4 text-accent-primary" />
            </div>
            <div>
              <CardTitle className="text-lg font-bold text-text-primary tracking-tight">
                Slips by Card Count
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Distribution of betting slips by number of cards over time
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-grow">
        <ChartContainer config={chartConfig} className="h-full w-full">
          {transformedData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={transformedData}
                margin={{ top: 20, right: 40, left: 30, bottom: isModal ? 80 : 20 }}
              >
                <XAxis
                  dataKey="period"
                  dy={isModal ? 15 : 0}
                  axisLine={false}
                  tickLine={false}
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
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: CHART_COLORS.axis.text, fontSize: 11 }}
                  tickFormatter={formatNumber}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  verticalAlign="top" 
                  height={36}
                  wrapperStyle={{ fontSize: '12px', color: CHART_COLORS.axis.text }}
                />
                
                {/* Create a bar for each card count */}
                {CARD_COUNTS.map((cardCount, index) => (
                  <Bar
                    key={`${cardCount}cards`}
                    dataKey={`${cardCount}cards`}
                    stackId="a"
                    fill={CHART_COLORS.cardCounts[index]}
                    name={`${cardCount} Card${cardCount !== 1 ? 's' : ''}`}
                    radius={index === CARD_COUNTS.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-text-secondary">
              <p>No data available</p>
            </div>
          )}
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
        {/* Border shine effect */}
        <div className="absolute inset-0 rounded-lg overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 transform -skew-x-12 -translate-x-full group-hover:translate-x-full" />
        </div>
        
        {/* Expand icon overlay */}
        <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="p-2 bg-bg-elevated/90 backdrop-blur-sm rounded-lg border border-border-subtle">
            <CreditCard className="w-4 h-4 text-accent-primary" />
          </div>
        </div>
        
        {content}
      </div>
    )
  }

  return content
}
