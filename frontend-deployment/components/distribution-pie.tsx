"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts"
import { Smartphone, Monitor, Tablet, Globe } from "lucide-react"

const distributionData = [
  {
    name: "Desktop",
    value: 45,
    color: "#D0FF12",
    icon: Monitor,
    sessions: "12.4k",
    growth: "+5.2%",
  },
  {
    name: "Mobile",
    value: 35,
    color: "#3B82F6",
    icon: Smartphone,
    sessions: "9.8k",
    growth: "+12.1%",
  },
  {
    name: "Tablet",
    value: 15,
    color: "#A855F7",
    icon: Tablet,
    sessions: "3.2k",
    growth: "-2.3%",
  },
  {
    name: "Other",
    value: 5,
    color: "rgba(248, 250, 252, 0.3)",
    icon: Globe,
    sessions: "1.1k",
    growth: "+0.8%",
  },
]

export function DistributionPie() {
  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20 flex-shrink-0">
                {" "}
                {/* Added flex-shrink-0 */}
                <Smartphone className="w-4 h-4 text-purple-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight max-w-[calc(100%-4rem)]">
                Traffic Sources
              </CardTitle>{" "}
              {/* Added max-w */}
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed max-w-full">
              {" "}
              {/* Adjusted max-w */}
              Device distribution and user engagement patterns
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="flex items-center gap-8">
          {/* Chart with enhanced styling */}
          <div className="flex-shrink-0">
            <ChartContainer
              config={{
                desktop: { label: "Desktop", color: "#D0FF12" },
                mobile: { label: "Mobile", color: "#3B82F6" },
                tablet: { label: "Tablet", color: "#A855F7" },
                other: { label: "Other", color: "rgba(248, 250, 252, 0.3)" },
              }}
              className="h-[200px] w-[200px]"
            >
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={distributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {distributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(0, 0, 0, 0.1)" strokeWidth={1} />
                    ))}
                  </Pie>
                  <ChartTooltip content={<ChartTooltipContent />} />
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </div>

          {/* Legend with enhanced details */}
          <div className="flex-1 space-y-4">
            {distributionData.map((item, index) => {
              const IconComponent = item.icon
              return (
                <div
                  key={item.name}
                  className={cn(
                    "flex items-center justify-between p-3 rounded-xl bg-bg-elevated border border-border-subtle hover:border-border-medium transition-all duration-300",
                    index % 2 === 1 ? "ml-3" : "mr-1", // Subtle asymmetry
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: item.color }} />
                      <IconComponent className="w-4 h-4 text-text-secondary" />
                    </div>
                    <div>
                      <p className="text-text-primary text-sm font-medium">{item.name}</p>
                      <p className="text-text-tertiary text-xs">{item.sessions} sessions</p>
                    </div>
                  </div>

                  <div className="text-right">
                    <p className="text-text-primary text-sm font-bold">{item.value}%</p>
                    <p
                      className={cn(
                        "text-xs font-medium",
                        item.growth.startsWith("+") ? "text-accent-primary" : "text-red-400",
                      )}
                    >
                      {item.growth}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Summary with organic positioning */}
        <div className="mt-6 pt-4 border-t border-border-subtle">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-text-tertiary text-xs font-medium uppercase tracking-wider">Total Sessions</p>
              <p className="text-text-primary text-lg font-bold">26.5k</p>
            </div>
            <div className="text-right">
              <p className="text-text-tertiary text-xs">Avg. Session Duration</p>
              <p className="text-text-primary text-sm font-semibold">4m 32s</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(" ")
}
