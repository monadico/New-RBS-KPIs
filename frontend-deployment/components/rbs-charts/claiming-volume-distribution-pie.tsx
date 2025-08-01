// components/rbs-charts/claiming-volume-distribution-pie.tsx
"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts"
import { PieChart as PieChartIcon } from "lucide-react"
import { formatCurrency } from "@/lib/utils"

interface ClaimingVolumeDistributionPieProps {
  monVolume: number
  jerryVolume: number
  onChartClick?: () => void
  isModal?: boolean
}

export function ClaimingVolumeDistributionPie({ monVolume, jerryVolume, onChartClick, isModal = false }: ClaimingVolumeDistributionPieProps) {
  const totalVolume = monVolume + jerryVolume

  // Prepare data for pie chart
  const pieData = [
    {
      name: "$MON Claimed",
      value: monVolume,
      color: "#D0FF12",
      percentage: totalVolume > 0 ? ((monVolume / totalVolume) * 100).toFixed(1) : "0"
    },
    {
      name: "$JERRY Claimed",
      value: jerryVolume,
      color: "#EC305D",
      percentage: totalVolume > 0 ? ((jerryVolume / totalVolume) * 100).toFixed(1) : "0"
    }
  ]

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-surface border border-border-subtle rounded-lg p-3 shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: data.color }}
            />
            <span className="text-text-primary font-medium">{data.name}</span>
          </div>
          <div className="space-y-1">
            <p className="text-text-secondary text-sm">
              Volume: {formatCurrency(data.value)}
            </p>
            <p className="text-text-secondary text-sm">
              Share: {data.percentage}%
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  // Custom legend
  const CustomLegend = ({ payload }: any) => (
    <div className="flex flex-col gap-2 mt-4">
      {payload?.map((entry: any, index: number) => (
        <div key={index} className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-text-secondary text-sm">{entry.value}</span>
          </div>
          <span className="text-text-primary text-sm font-medium">
            {formatCurrency(entry.payload.value)}
          </span>
        </div>
      ))}
    </div>
  )

  // Create standalone chart for modal mode
  const modalChart = (
    <div className="w-full h-[450px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={120}
            paddingAngle={5}
            dataKey="value"
          >
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )

  const content = (
    <>
      {!isModal && (
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent-muted rounded-lg border border-accent-primary/20">
                <PieChartIcon className="w-4 h-4 text-accent-primary" />
              </div>
              <div>
                <CardTitle className="text-lg font-bold text-text-primary tracking-tight">
                  Claiming Volume Distribution
                </CardTitle>
                <CardDescription className="text-text-secondary">
                  Distribution of claimed tokens by type
                </CardDescription>
              </div>
            </div>
          </div>
        </CardHeader>
      )}

      <CardContent className={isModal ? "p-0" : ""}>
        <div className={`${isModal ? "h-[450px]" : "h-[400px]"} w-full`}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={isModal ? 60 : 50}
                outerRadius={isModal ? 120 : 100}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend content={<CustomLegend />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </>
  )

  // If this is for modal display, return standalone chart
  if (isModal) {
    return modalChart
  }

  // For regular display, wrap in clickable card
  if (onChartClick) {
    return (
      <div 
        className="cursor-pointer transition-all duration-200 group hover:scale-[1.02] hover:shadow-glow-medium relative"
        onClick={onChartClick}
      >
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-accent-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 rounded-lg" />
        
        {/* Expand icon overlay */}
        <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="p-2 bg-bg-elevated/90 backdrop-blur-sm rounded-lg border border-border-subtle">
            <PieChartIcon className="w-4 h-4 text-accent-primary" />
          </div>
        </div>
        
        <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500">
          {content}
        </Card>
      </div>
    )
  }

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500">
      {content}
    </Card>
  )
} 