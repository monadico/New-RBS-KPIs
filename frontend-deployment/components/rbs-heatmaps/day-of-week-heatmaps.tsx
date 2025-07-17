// components/rbs-heatmaps/day-of-week-heatmaps.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Calendar } from "lucide-react"
import { getHeatmapColor, formatNumber, formatCurrency } from "@/lib/utils"
import type { PeriodData } from "@/lib/data-types"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface DayOfWeekHeatmapsProps {
  data: PeriodData[]
}

export function DayOfWeekHeatmaps({ data }: DayOfWeekHeatmapsProps) {
  const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

  // Aggregate data by day of week
  const aggregateByDay = (key: keyof PeriodData) => {
    const aggregated: { [key: string]: number } = {}
    daysOfWeek.forEach((day) => (aggregated[day] = 0))

    data.forEach((period) => {
      // Each period represents a single day, so we use the start_date directly
      const date = new Date(period.start_date)
      
      // getDay() returns 0=Sunday, 1=Monday, ..., 6=Saturday
      // We want 0=Monday, 1=Tuesday, ..., 6=Sunday
      const dayIndex = date.getDay() === 0 ? 6 : date.getDay() - 1
      
      // Add the actual value for this day
      aggregated[daysOfWeek[dayIndex]] += period[key] as number
    })
    return aggregated
  }

  const submissionsByDay = aggregateByDay("submissions")
  const monVolumeByDay = aggregateByDay("mon_volume")
  const jerryVolumeByDay = aggregateByDay("jerry_volume")

  const maxSubmission = Math.max(...Object.values(submissionsByDay))
  const maxMonVolume = Math.max(...Object.values(monVolumeByDay))
  const maxJerryVolume = Math.max(...Object.values(jerryVolumeByDay))

  const HeatmapBar = ({
    label,
    value,
    maxValue,
    formatter,
  }: {
    label: string
    value: number
    maxValue: number
    formatter: (num: number) => string
  }) => (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="flex flex-col items-center gap-2 h-full justify-end cursor-pointer">
          <div
            className="w-8 rounded-md transition-all duration-300 hover:scale-105"
            style={{ 
              backgroundColor: getHeatmapColor(value, maxValue), 
              height: `${Math.max((value / maxValue) * 100, 4)}%` 
            }}
          />
          <span className="text-text-tertiary text-xs">{label.substring(0, 3)}</span>
        </div>
      </TooltipTrigger>
      <TooltipContent className="bg-bg-elevated border-border-medium text-text-primary">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-text-secondary text-xs">{formatter(value)}</p>
      </TooltipContent>
    </Tooltip>
  )

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group lg:col-span-full">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500/10 rounded-lg border border-orange-500/20">
                <Calendar className="w-4 h-4 text-orange-400" />
              </div>
              <CardTitle className="text-lg font-bold text-text-primary tracking-tight">Day of Week Activity</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Activity and volume aggregated by day of the week
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <TooltipProvider>
          {/* Submissions by Day */}
          <div className="bg-bg-elevated p-4 rounded-xl border border-border-subtle">
            <h3 className="text-text-primary text-base font-semibold mb-4">Submissions</h3>
            <div className="flex justify-around items-end h-32">
              {daysOfWeek.map((day) => (
                <HeatmapBar
                  key={day}
                  label={day}
                  value={submissionsByDay[day]}
                  maxValue={maxSubmission}
                  formatter={formatNumber}
                />
              ))}
            </div>
          </div>

          {/* $MON Volume by Day */}
          <div className="bg-bg-elevated p-4 rounded-xl border border-border-subtle">
            <h3 className="text-text-primary text-base font-semibold mb-4">$MON Volume</h3>
            <div className="flex justify-around items-end h-32">
              {daysOfWeek.map((day) => (
                <HeatmapBar
                  key={day}
                  label={day}
                  value={monVolumeByDay[day]}
                  maxValue={maxMonVolume}
                  formatter={formatCurrency}
                />
              ))}
            </div>
          </div>

          {/* $JERRY Volume by Day */}
          <div className="bg-bg-elevated p-4 rounded-xl border border-border-subtle">
            <h3 className="text-text-primary text-base font-semibold mb-4">$JERRY Volume</h3>
            <div className="flex justify-around items-end h-32">
              {daysOfWeek.map((day) => (
                <HeatmapBar
                  key={day}
                  label={day}
                  value={jerryVolumeByDay[day]}
                  maxValue={maxJerryVolume}
                  formatter={formatCurrency}
                />
              ))}
            </div>
          </div>
        </TooltipProvider>
      </CardContent>
    </Card>
  )
}
