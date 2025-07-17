// components/rbs-charts/slips-by-card-stacked-bar.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts"
import { Layers } from "lucide-react"
import type { TimeframeCardCounts } from "@/lib/data-types"
import { formatNumber } from "../../lib/utils"

interface SlipsByCardStackedBarProps {
  data: TimeframeCardCounts[]
}

const COLORS = ["#D12#9EF909", "#F07632", "#EC305D", "#1E90FF", "#5DD070"]
const CARD_COUNTS = [2, 3, 4, 5, 6, 7]

export function SlipsByCardStackedBar({ data }: SlipsByCardStackedBarProps) {
  // Transform data for stacked bar chart
  const transformedData = data.map((period, index) => {
    const result: any = {
      period: period.period_start,
      periodNumber: period.period_number
    }
    
    // Add each card count as a separate data point
    CARD_COUNTS.forEach((cardCount, cardIndex) => {
      result[`${cardCount}cards`] = period.card_counts[cardIndex] || 0
    })
    
    return result
  })

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-bg-elevated border border-border-medium rounded-lg p-3 shadow-lg">
          <p className="text-text-primary font-medium mb-2">Period: {label}</p>
          <div className="space-y-1">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-sm" 
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-text-secondary text-sm">
                  {entry.name}: {formatNumber(entry.value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group lg:col-span-2">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <Layers className="w-4 h-4 text-blue-400" />
              </div>
              <CardTitle className="text-lg font-bold text-text-primary tracking-tight">
                Slips by Card Count
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Distribution of slips based on number of cards over time
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="h-[500px] w-full">
          {transformedData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={transformedData}
                margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
              >
                <XAxis
                  dataKey="period"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "white", fontSize: 11 }}
                  tickFormatter={(value) => {
                    const date = new Date(value)
                    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
                  }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "white", fontSize: 11 }}
                  tickFormatter={formatNumber}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  verticalAlign="top" 
                  height={36}
                  wrapperStyle={{ fontSize: '12px', color: 'white' }}
                />
                
                {/* Create a bar for each card count */}
                {CARD_COUNTS.map((cardCount, index) => (
                  <Bar
                    key={`${cardCount}cards`}
                    dataKey={`${cardCount}cards`}
                    stackId="a"
                    fill={COLORS[index]}
                    name={`${cardCount} Cards`}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-text-secondary">
              <p>No data available</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
