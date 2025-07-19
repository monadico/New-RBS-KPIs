// components/rbs-charts/overall-slips-pie.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Cell, Pie, PieChart } from "recharts"
import { PieChartIcon } from "lucide-react"
import type { SlipCardCount } from "@/lib/data-types"
import { formatNumber } from "@/lib/utils"

interface OverallSlipsPieProps {
  data: SlipCardCount[]
}

const COLORS = ["#D12#9EF909", "#F07632", "#EC305D", "#1E90FF"]

export function OverallSlipsPie({ data }: OverallSlipsPieProps) {
  const totalBets = data.reduce((sum, item) => sum + item.bets, 0)

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group h-full">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
                <PieChartIcon className="w-4 h-4 text-purple-400" />
              </div>
              <CardTitle className="text-lg font-bold text-text-primary tracking-tight">Slip Distribution</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Distribution of slips by card count
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex flex-col items-center gap-4">
        {/* Chart */}
        <div className="relative">
          <PieChart width={220} height={220}>
            <Pie 
              data={data} 
              cx="50%" 
              cy="50%" 
              innerRadius={50} 
              outerRadius={80} 
              paddingAngle={2} 
              dataKey="bets"
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                  stroke="rgba(255, 255, 255, 0.1)"
                  strokeWidth={1}
                />
              ))}
            </Pie>
          </PieChart>
          
          {/* Center total */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <p className="text-text-tertiary text-xs font-medium">Total</p>
              <p className="text-text-primary text-lg font-bold">{formatNumber(totalBets)}</p>
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="w-full space-y-2">
          {data.map((item, index) => (
            <div
              key={item.cards_in_slip}
              className="flex items-center justify-between p-2 rounded-lg bg-bg-elevated border border-border-subtle hover:border-border-medium transition-all duration-200"
            >
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-text-primary text-sm font-medium">{item.cards_in_slip} Cards</span>
              </div>
              <div className="text-right">
                <p className="text-text-primary text-sm font-bold">{item.percentage}%</p>
                <p className="text-text-tertiary text-xs">{formatNumber(item.bets)}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
