"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

interface ClaimingActivityTimelineProps {
  data: any[]
  onChartClick?: () => void
  isModal?: boolean
}

export function ClaimingActivityTimeline({ data, onChartClick, isModal = false }: ClaimingActivityTimelineProps) {
  // Placeholder data structure - will be updated when claiming data is available
  const chartData = data.length > 0 ? data : [
    { date: "2024-01", transactions: 0, unique_users: 0 },
    { date: "2024-02", transactions: 0, unique_users: 0 },
    { date: "2024-03", transactions: 0, unique_users: 0 },
  ]

  return (
    <Card className={`${isModal ? '' : 'cursor-pointer hover:shadow-lg transition-shadow'}`} onClick={onChartClick}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Claiming Activity Timeline</CardTitle>
        <CardDescription>Claiming transactions and unique users over time</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Bar yAxisId="left" dataKey="transactions" fill="#8884d8" name="Transactions" />
            <Bar yAxisId="right" dataKey="unique_users" fill="#82ca9d" name="Unique Users" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
} 