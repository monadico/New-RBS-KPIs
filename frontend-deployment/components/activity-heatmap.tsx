"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Calendar, TrendingUp } from "lucide-react"
import { useState } from "react"

// Generate sophisticated heatmap data
const generateHeatmapData = () => {
  const data = []
  const days = ["S", "M", "T", "W", "T", "F", "S"]
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

  for (let week = 0; week < 52; week++) {
    for (let day = 0; day < 7; day++) {
      const monthIndex = Math.floor(week / 4.33)
      const intensity = Math.random()
      const value = Math.floor(intensity * 5)

      data.push({
        week,
        day,
        dayName: days[day],
        month: months[monthIndex] || "Dec",
        value,
        intensity,
        activities: Math.floor(intensity * 25),
      })
    }
  }
  return data
}

const heatmapData = generateHeatmapData()

const getIntensityColor = (value: number) => {
  const intensities = [
    "rgba(248, 250, 252, 0.05)",
    "rgba(208, 255, 18, 0.15)",
    "rgba(208, 255, 18, 0.35)",
    "rgba(208, 255, 18, 0.55)",
    "rgba(208, 255, 18, 0.75)",
  ]
  return intensities[value] || intensities[0]
}

export function ActivityHeatmap() {
  const [hoveredCell, setHoveredCell] = useState<any>(null)

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent-muted rounded-lg">
                <Calendar className="w-4 h-4 text-accent-primary" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">Activity Timeline</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              User engagement patterns throughout the year with intensity mapping
            </CardDescription>
          </div>

          {/* Stats summary */}
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-text-tertiary text-xs font-medium uppercase tracking-wider">Total Activities</p>
              <p className="text-text-primary text-lg font-bold">2,847</p>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-muted rounded-lg">
              <TrendingUp className="w-3.5 h-3.5 text-accent-primary" />
              <span className="text-xs font-semibold text-accent-primary">+23%</span>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Month labels with asymmetrical spacing */}
        <div className="mb-4">
          <div className="grid grid-cols-12 gap-2 mb-2">
            {" "}
            {/* Increased gap */}
            {["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].map(
              (month, index) => (
                <div
                  key={month}
                  className={cn(
                    "text-2xs text-text-tertiary font-medium text-center",
                    index % 3 === 0 ? "text-text-secondary" : "",
                    "col-span-1", // Ensure each month takes one column, let grid handle spacing
                  )}
                >
                  {month}
                </div>
              ),
            )}
          </div>
        </div>

        {/* Heatmap grid */}
        <div className="space-y-1">
          {["S", "M", "T", "W", "T", "F", "S"].map((day, dayIndex) => (
            <div key={day} className="flex items-center gap-2">
              <div className="w-4 text-2xs text-text-tertiary font-medium">{day}</div>
              <div className="grid grid-cols-52 gap-0.5 flex-1">
                {Array.from({ length: 52 }, (_, week) => {
                  const dataPoint = heatmapData.find((d) => d.week === week && d.day === dayIndex)
                  return (
                    <div
                      key={`${week}-${dayIndex}`}
                      className="w-3 h-3 rounded-sm transition-all duration-200 hover:scale-125 hover:z-10 relative cursor-pointer border border-transparent hover:border-accent-primary/30" // Increased size
                      style={{
                        backgroundColor: getIntensityColor(dataPoint?.value || 0),
                      }}
                      onMouseEnter={() => setHoveredCell(dataPoint)}
                      onMouseLeave={() => setHoveredCell(null)}
                    />
                  )
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Enhanced legend and tooltip */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-border-subtle">
          <div className="flex items-center gap-4">
            <span className="text-2xs text-text-tertiary font-medium">Less</span>
            <div className="flex gap-1">
              {[0, 1, 2, 3, 4].map((level) => (
                <div
                  key={level}
                  className="w-2.5 h-2.5 rounded-sm border border-border-subtle"
                  style={{ backgroundColor: getIntensityColor(level) }}
                />
              ))}
            </div>
            <span className="text-2xs text-text-tertiary font-medium">More</span>
          </div>

          {/* Hover tooltip */}
          {hoveredCell && (
            <div className="px-3 py-2 bg-bg-elevated rounded-lg border border-border-medium animate-scale-in">
              <p className="text-text-primary text-xs font-medium">{hoveredCell.activities} activities</p>
              <p className="text-text-tertiary text-2xs">
                Week {hoveredCell.week + 1}, {hoveredCell.dayName}
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(" ")
}
