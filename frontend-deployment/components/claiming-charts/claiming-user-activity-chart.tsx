"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

interface ClaimingUserActivityChartProps {
  data: any[]
  onChartClick?: () => void
  isModal?: boolean
}

export function ClaimingUserActivityChart({ data, onChartClick, isModal = false }: ClaimingUserActivityChartProps) {
  // Placeholder data structure - will be updated when claiming data is available
  const chartData = data.length > 0 ? data : [
    { date: "2024-01", active_claimers: 0, new_claimers: 0 },
    { date: "2024-02", active_claimers: 0, new_claimers: 0 },
    { date: "2024-03", active_claimers: 0, new_claimers: 0 },
  ]

  return (
    <Card className={`${isModal ? '' : 'cursor-pointer hover:shadow-lg transition-shadow'}`} onClick={onChartClick}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">User Activity</CardTitle>
        <CardDescription>Active and new claimers over time</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="active_claimers" 
              stroke="#8884d8" 
              strokeWidth={2}
              name="Active Claimers"
            />
            <Line 
              type="monotone" 
              dataKey="new_claimers" 
              stroke="#82ca9d" 
              strokeWidth={2}
              name="New Claimers"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
} 