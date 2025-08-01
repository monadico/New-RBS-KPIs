"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"

interface ClaimingTokenDistributionPieProps {
  data: any[]
  onChartClick?: () => void
  isModal?: boolean
}

export function ClaimingTokenDistributionPie({ data, onChartClick, isModal = false }: ClaimingTokenDistributionPieProps) {
  // Placeholder data structure - will be updated when claiming data is available
  const chartData = data.length > 0 ? data : [
    { name: "MON", value: 0, color: "#8884d8" },
    { name: "JERRY", value: 0, color: "#82ca9d" },
  ]

  return (
    <Card className={`${isModal ? '' : 'cursor-pointer hover:shadow-lg transition-shadow'}`} onClick={onChartClick}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Token Distribution</CardTitle>
        <CardDescription>MON vs JERRY claiming transactions</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
} 