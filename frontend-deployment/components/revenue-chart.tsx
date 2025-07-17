"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Line, ResponsiveContainer, XAxis, YAxis, Area, AreaChart } from "recharts"
import { TrendingUp, Calendar } from "lucide-react"

const revenueData = [
  { month: "Jan", revenue: 45000, target: 50000, growth: 42000 },
  { month: "Feb", revenue: 52000, target: 55000, growth: 48000 },
  { month: "Mar", revenue: 48000, target: 52000, growth: 51000 },
  { month: "Apr", revenue: 61000, target: 58000, growth: 55000 },
  { month: "May", revenue: 55000, target: 60000, growth: 58000 },
  { month: "Jun", revenue: 67000, target: 65000, growth: 62000 },
  { month: "Jul", revenue: 72000, target: 70000, growth: 68000 },
  { month: "Aug", revenue: 69000, target: 72000, growth: 71000 },
  { month: "Sep", revenue: 78000, target: 75000, growth: 75000 },
  { month: "Oct", revenue: 82000, target: 80000, growth: 79000 },
  { month: "Nov", revenue: 87000, target: 85000, growth: 84000 },
  { month: "Dec", revenue: 94000, target: 90000, growth: 89000 },
]

export function RevenueChart() {
  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group overflow-hidden">
      {/* Ambient glow effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-accent-muted/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

      <CardHeader className="relative pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent-muted rounded-lg">
                <TrendingUp className="w-4 h-4 text-accent-primary" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">Revenue Analytics</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed max-w-md">
              Monthly performance tracking with predictive insights and target comparisons
            </CardDescription>
          </div>

          {/* Time period indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-bg-elevated rounded-lg border border-border-subtle">
            <Calendar className="w-3.5 h-3.5 text-text-tertiary" />
            <span className="text-xs font-medium text-text-secondary">2024</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="relative pt-4">
        <ChartContainer
          config={{
            revenue: {
              label: "Revenue",
              color: "#D0FF12",
            },
            target: {
              label: "Target",
              color: "rgba(255, 255, 255, 0.3)",
            },
            growth: {
              label: "Growth Area",
              color: "rgba(208, 255, 18, 0.1)",
            },
          }}
          className="h-[320px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={revenueData} margin={{ top: 20, right: 40, left: 30, bottom: 20 }}>
              <defs>
                <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="rgba(208, 255, 18, 0.2)" />
                  <stop offset="100%" stopColor="rgba(208, 255, 18, 0.02)" />
                </linearGradient>
              </defs>

              <XAxis
                dataKey="month"
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
                tickFormatter={(value) => `$${value / 1000}k`}
                dx={-15}
              />

              <ChartTooltip
                content={<ChartTooltipContent />}
                cursor={{ stroke: "rgba(208, 255, 18, 0.2)", strokeWidth: 1 }}
              />

              {/* Area fill */}
              <Area type="monotone" dataKey="revenue" stroke="none" fill="url(#revenueGradient)" />

              {/* Main revenue line */}
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#D0FF12"
                strokeWidth={3}
                dot={{
                  fill: "#D0FF12",
                  strokeWidth: 0,
                  r: 4,
                  filter: "drop-shadow(0 0 6px rgba(208, 255, 18, 0.6))",
                }}
                activeDot={{
                  r: 6,
                  stroke: "#D0FF12",
                  strokeWidth: 2,
                  fill: "#1A1D24",
                  filter: "drop-shadow(0 0 8px rgba(208, 255, 18, 0.8))",
                }}
              />

              {/* Target line */}
              <Line
                type="monotone"
                dataKey="target"
                stroke="rgba(248, 250, 252, 0.3)"
                strokeWidth={2}
                strokeDasharray="6 4"
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartContainer>

        {/* Summary stats with asymmetrical layout */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-border-subtle">
          <div className="flex items-center gap-6">
            <div>
              <p className="text-text-tertiary text-xs font-medium uppercase tracking-wider">Total Revenue</p>
              <p className="text-text-primary text-lg font-bold">$847,392</p>
            </div>
            <div>
              <p className="text-text-tertiary text-xs font-medium uppercase tracking-wider">Avg Growth</p>
              <p className="text-accent-primary text-lg font-bold">+12.4%</p>
            </div>
          </div>

          <div className="text-right">
            <p className="text-text-tertiary text-xs">Target Achievement</p>
            <p className="text-text-primary text-sm font-semibold">94.2%</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
