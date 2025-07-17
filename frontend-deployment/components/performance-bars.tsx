"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { Activity, ArrowUpRight } from "lucide-react"

const performanceData = [
  { category: "Sales", current: 85, previous: 78, team: "12 members" },
  { category: "Marketing", current: 72, previous: 65, team: "8 members" },
  { category: "Support", current: 91, previous: 88, team: "15 members" },
  { category: "Development", current: 68, previous: 72, team: "22 members" },
  { category: "Operations", current: 79, previous: 75, team: "6 members" },
]

export function PerformanceBars() {
  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <Activity className="w-4 h-4 text-blue-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">Team Performance</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Department efficiency metrics and quarterly comparisons
            </CardDescription>
          </div>

          {/* Performance indicator */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-muted rounded-lg">
            <ArrowUpRight className="w-3.5 h-3.5 text-accent-primary" />
            <span className="text-xs font-semibold text-accent-primary">+8.2%</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-2">
        <ChartContainer
          config={{
            current: {
              label: "Current Quarter",
              color: "#D0FF12",
            },
            previous: {
              label: "Previous Quarter",
              color: "rgba(248, 250, 252, 0.2)",
            },
          }}
          className="h-[280px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={performanceData} barGap={8} margin={{ top: 20, right: 40, left: 30, bottom: 20 }}>
              <XAxis
                dataKey="category"
                axisLine={false}
                tickLine={false}
                tick={{
                  fill: "rgba(248, 250, 252, 0.4)",
                  fontSize: 11,
                  fontWeight: 500,
                }}
                dy={10}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{
                  fill: "rgba(248, 250, 252, 0.4)",
                  fontSize: 11,
                  fontWeight: 500,
                }}
                domain={[0, 100]}
                dx={-15}
              />
              <ChartTooltip content={<ChartTooltipContent />} cursor={{ fill: "rgba(255, 255, 255, 0.02)" }} />

              <Bar dataKey="previous" fill="rgba(248, 250, 252, 0.15)" radius={[6, 6, 0, 0]} maxBarSize={40} />
              <Bar dataKey="current" fill="#D0FF12" radius={[6, 6, 0, 0]} maxBarSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>

        {/* Department details with organic spacing */}
        <div className="grid grid-cols-2 gap-4 mt-6 pt-4 border-t border-border-subtle">
          {performanceData.slice(0, 4).map((dept, index) => (
            <div
              key={dept.category}
              className={cn(
                "flex items-center justify-between p-3 rounded-lg bg-bg-elevated border border-border-subtle",
                index % 2 === 0 ? "mr-2" : "ml-2", // Subtle asymmetry
              )}
            >
              <div>
                <p className="text-text-primary text-sm font-medium">{dept.category}</p>
                <p className="text-text-tertiary text-xs">{dept.team}</p>
              </div>
              <div className="text-right">
                <p className="text-text-primary text-sm font-bold">{dept.current}%</p>
                <p
                  className={cn(
                    "text-xs font-medium",
                    dept.current > dept.previous ? "text-accent-primary" : "text-red-400",
                  )}
                >
                  {dept.current > dept.previous ? "+" : ""}
                  {dept.current - dept.previous}%
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(" ")
}
