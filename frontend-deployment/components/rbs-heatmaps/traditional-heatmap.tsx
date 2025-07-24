// components/rbs-heatmaps/traditional-heatmap.tsx
"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar, TrendingUp, DollarSign } from "lucide-react"
import { getHeatmapColor, formatNumber, formatCurrency } from "@/lib/utils"
import type { PeriodData } from "@/lib/data-types"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface TraditionalHeatmapProps {
  data: PeriodData[]
}

interface CalendarDay {
  date: string
  submissions: number
  monVolume: number
  jerryVolume: number
}

type MetricType = "submissions" | "mon" | "jerry"

export function TraditionalHeatmap({ data }: TraditionalHeatmapProps) {
  const [selectedMetric, setSelectedMetric] = useState<MetricType>("submissions")

  // Process data into calendar format
  const processCalendarData = (): CalendarDay[] => {
    const calendarData: { [key: string]: CalendarDay } = {}
    
    data.forEach((period) => {
      const date = period.start_date
      calendarData[date] = {
        date,
        submissions: period.submissions,
        monVolume: period.mon_volume,
        jerryVolume: period.jerry_volume
      }
    })
    
    return Object.values(calendarData).sort((a, b) => {
      const [yearA, monthA, dayA] = a.date.split('-').map(Number)
      const [yearB, monthB, dayB] = b.date.split('-').map(Number)
      const dateA = new Date(yearA, monthA - 1, dayA)
      const dateB = new Date(yearB, monthB - 1, dayB)
      return dateA.getTime() - dateB.getTime()
    })
  }

  const calendarData = processCalendarData()
  
  // Calculate max values for color scaling
  const maxSubmissions = Math.max(...calendarData.map(d => d.submissions))
  const maxMonVolume = Math.max(...calendarData.map(d => d.monVolume))
  const maxJerryVolume = Math.max(...calendarData.map(d => d.jerryVolume))

  // Group data by weeks
  const groupByWeeks = () => {
    const weeks: { [key: string]: CalendarDay[] } = {}
    
    calendarData.forEach(day => {
      const [year, month, dayNum] = day.date.split('-').map(Number)
      const date = new Date(year, month - 1, dayNum)
      const weekStart = new Date(date)
      weekStart.setDate(date.getDate() - date.getDay()) // Start of week (Sunday)
      const weekKey = weekStart.toISOString().split('T')[0]
      
      if (!weeks[weekKey]) {
        weeks[weekKey] = []
      }
      weeks[weekKey].push(day)
    })
    
    return weeks
  }

  const weeks = groupByWeeks()
  const weekKeys = Object.keys(weeks).sort()

  // Get current metric data and max value
  const getMetricData = () => {
    switch (selectedMetric) {
      case "submissions":
        return {
          getValue: (day: CalendarDay) => day.submissions,
          maxValue: maxSubmissions,
          formatter: formatNumber,
          colorType: "green-red" as const,
          label: "Submissions"
        }
      case "mon":
        return {
          getValue: (day: CalendarDay) => day.monVolume,
          maxValue: maxMonVolume,
          formatter: formatCurrency,
          colorType: "blue-yellow" as const,
          label: "$MON Volume"
        }
      case "jerry":
        return {
          getValue: (day: CalendarDay) => day.jerryVolume,
          maxValue: maxJerryVolume,
          formatter: formatCurrency,
          colorType: "blue-yellow" as const,
          label: "$JERRY Volume"
        }
    }
  }

  const metricData = getMetricData()

  // Generate color legend
  const generateLegend = () => {
    const maxValue = metricData.maxValue
    const steps = [0, 0.25, 0.5, 0.75, 1]
    
    return (
      <div className="flex items-center gap-1 text-xs text-text-secondary">
        <span className="text-[10px]">Less</span>
        {steps.map((step, index) => {
          const value = step * maxValue
          const color = getHeatmapColor(value, maxValue, metricData.colorType)
          return (
            <div
              key={index}
              className="w-2 h-2 rounded-[1px]"
              style={{ backgroundColor: color }}
            />
          )
        })}
        <span className="text-[10px]">More</span>
      </div>
    )
  }

  const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500/10 rounded-lg border border-orange-500/20">
                <Calendar className="w-4 h-4 text-orange-400" />
              </div>
              <CardTitle className="text-lg font-bold text-text-primary tracking-tight">Activity Heatmap</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Daily activity visualization with metric toggling
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Metric Toggle */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex gap-1">
            <Button
              variant={selectedMetric === "submissions" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedMetric("submissions")}
              className="text-xs px-2 py-1 h-7"
            >
              <TrendingUp className="w-3 h-3 mr-1" />
              Submissions
            </Button>
            <Button
              variant={selectedMetric === "mon" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedMetric("mon")}
              className="text-xs px-2 py-1 h-7"
            >
              <DollarSign className="w-3 h-3 mr-1" />
              $MON
            </Button>
            <Button
              variant={selectedMetric === "jerry" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedMetric("jerry")}
              className="text-xs px-2 py-1 h-7"
            >
              <DollarSign className="w-3 h-3 mr-1" />
              $JERRY
            </Button>
          </div>
          {generateLegend()}
        </div>

        {/* Heatmap Grid */}
        <TooltipProvider>
          <div className="overflow-x-auto">
            <div className="max-w-4xl mx-auto">
              <div className="grid grid-cols-8 gap-[1px]">
                {/* Header row with day labels */}
                <div className="h-6" /> {/* Empty corner */}
                {daysOfWeek.map(day => (
                  <div key={day} className="h-6 flex items-center justify-center text-text-tertiary text-xs font-medium">
                    {day}
                  </div>
                ))}
                
                {/* Week rows */}
                {weekKeys.map(weekKey => {
                  const weekDays = weeks[weekKey]
                  const weekStart = new Date(weekKey)
                  const weekLabel = `${weekStart.getMonth() + 1}/${weekStart.getDate()}`
                  
                  return (
                    <div key={weekKey} className="contents">
                      {/* Week label */}
                      <div className="h-4 w-12 flex items-center justify-end pr-1 text-text-tertiary text-xs">
                        {weekLabel}
                      </div>
                      
                      {/* Day cells for this week */}
                      {daysOfWeek.map((_, dayIndex) => {
                        const targetDate = new Date(weekStart)
                        targetDate.setDate(weekStart.getDate() + dayIndex)
                        const dateStr = targetDate.toISOString().split('T')[0]
                        
                        const dayData = weekDays.find(d => d.date === dateStr)
                        const value = dayData ? metricData.getValue(dayData) : 0
                        const color = getHeatmapColor(value, metricData.maxValue, metricData.colorType)
                        
                        return (
                          <Tooltip key={`${weekKey}-${dayIndex}`}>
                            <TooltipTrigger asChild>
                              <div
                                className="aspect-square rounded-[1px] cursor-pointer transition-all duration-200 hover:scale-110 hover:border hover:border-border-medium"
                                style={{ 
                                  backgroundColor: color,
                                  width: 'clamp(8px, 2.5vw, 22px)',
                                  height: 'clamp(8px, 2.5vw, 22px)'
                                }}
                              />
                            </TooltipTrigger>
                            <TooltipContent className="bg-bg-elevated border-border-medium text-text-primary">
                              <p className="text-sm font-medium">{new Date(dateStr + 'T00:00:00').toLocaleDateString()}</p>
                              <p className="text-text-secondary text-xs">
                                {metricData.label}: {metricData.formatter(value)}
                              </p>
                              {dayData && (
                                <div className="text-text-secondary text-xs space-y-1 mt-2 pt-2 border-t border-border-subtle">
                                  <p>Submissions: {formatNumber(dayData.submissions)}</p>
                                  <p>$MON: {formatCurrency(dayData.monVolume)}</p>
                                  <p>$JERRY: {formatCurrency(dayData.jerryVolume)}</p>
                                </div>
                              )}
                            </TooltipContent>
                          </Tooltip>
                        )
                      })}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </TooltipProvider>
      </CardContent>
    </Card>
  )
} 