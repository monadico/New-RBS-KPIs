"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts"
import { Trophy, XCircle } from "lucide-react"
import { useState, useEffect } from "react"

interface WinrateData {
  labels: string[]
  datasets: Array<{
    data: number[]
    backgroundColor: string[]
    borderColor: string[]
    borderWidth: number
  }>
  winrate_percentage: number
  total_bets: number
}

interface WinratePieChartProps {
  winrateData: WinrateData | null
  loading?: boolean
  error?: string | null
}

export function WinratePieChart({ winrateData, loading = false, error = null }: WinratePieChartProps) {

  if (loading) {
    return (
      <Card className="bg-surface border-border-subtle shadow-card-medium">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl font-bold text-text-primary">Winrate Analytics</CardTitle>
          <CardDescription className="text-text-secondary">Loading winrate data...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px]">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-accent-primary"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !winrateData) {
    return (
      <Card className="bg-surface border-border-subtle shadow-card-medium">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl font-bold text-text-primary">Winrate Analytics</CardTitle>
          <CardDescription className="text-text-secondary">Error loading data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-text-secondary">
            {error || 'No data available'}
          </div>
        </CardContent>
      </Card>
    )
  }

  // Transform data for the pie chart
  const chartData = winrateData.labels.map((label, index) => ({
    name: label,
    value: winrateData.datasets[0].data[index],
    color: winrateData.datasets[0].backgroundColor[index],
    icon: label === 'Won' ? Trophy : XCircle,
    percentage: ((winrateData.datasets[0].data[index] / winrateData.total_bets) * 100).toFixed(1),
  }))

  return (
    <Card className="h-full bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500/10 rounded-lg border border-green-500/20 flex-shrink-0">
                <Trophy className="w-4 h-4 text-green-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight max-w-[calc(100%-4rem)]">
                Winrate Analytics
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed max-w-full">
              Overall winrate based on claimed vs unclaimed bets
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="h-full flex flex-col">
        {/* Mobile: Vertical layout with legend below */}
        <div className="h-[400px] sm:h-[400px] w-full flex flex-col sm:flex-row items-center gap-4">
          {/* Chart */}
          <div className="flex-1 h-full min-w-0">
            <ChartContainer
              config={{
                Won: { label: "Won", color: "#4CAF50" },
                "Lost/Undecided": { label: "Lost/Undecided", color: "#FF5722" },
              }}
              className="h-full w-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(0, 0, 0, 0.1)" strokeWidth={1} />
                    ))}
                  </Pie>
                  <ChartTooltip content={<ChartTooltipContent />} />
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </div>

          {/* Legend - Mobile: below chart, Desktop: beside chart */}
          <div className="flex-1 space-y-2 min-w-0 w-full sm:w-auto">
            {chartData.map((item, index) => {
              const IconComponent = item.icon
              return (
                <div
                  key={item.name}
                  className="flex items-center justify-between p-2 rounded-lg bg-bg-elevated border border-border-subtle hover:border-border-medium transition-all duration-300 w-full"
                >
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <div className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: item.color }} />
                      <IconComponent className="w-3 h-3 text-text-secondary" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-text-primary text-xs font-medium truncate">{item.name}</p>
                      <p className="text-text-tertiary text-xs truncate">{item.value.toLocaleString()} bets</p>
                    </div>
                  </div>

                  <div className="text-right flex-shrink-0 ml-2">
                    <p className="text-text-primary text-xs font-bold">{item.percentage}%</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(" ")
} 