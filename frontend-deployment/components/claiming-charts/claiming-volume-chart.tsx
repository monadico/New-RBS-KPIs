"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

interface ClaimingVolumeChartProps {
  data: any[]
  onChartClick?: () => void
  isModal?: boolean
}

export function ClaimingVolumeChart({ data, onChartClick, isModal = false }: ClaimingVolumeChartProps) {
  // Placeholder data structure - will be updated when claiming data is available
  const chartData = data.length > 0 ? data : [
    { date: "2024-01", mon_volume: 0, jerry_volume: 0 },
    { date: "2024-02", mon_volume: 0, jerry_volume: 0 },
    { date: "2024-03", mon_volume: 0, jerry_volume: 0 },
  ]

  return (
    <Card className={`${isModal ? '' : 'cursor-pointer hover:shadow-lg transition-shadow'}`} onClick={onChartClick}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Claiming Volume</CardTitle>
        <CardDescription>MON and JERRY claiming volumes over time</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Area 
              type="monotone" 
              dataKey="mon_volume" 
              stackId="1" 
              stroke="#8884d8" 
              fill="#8884d8" 
              name="MON Volume"
            />
            <Area 
              type="monotone" 
              dataKey="jerry_volume" 
              stackId="1" 
              stroke="#82ca9d" 
              fill="#82ca9d" 
              name="JERRY Volume"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
} 