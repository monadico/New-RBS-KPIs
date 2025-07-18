import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Data formatting utilities (matching frontend2 logic)
export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  }
  return num.toLocaleString()
}

export const formatCurrency = (num: number): string => {
  return `$${num.toLocaleString()}`
}

export const formatDecimal = (num: number): string => {
  return num.toFixed(1)
}

export const formatAddress = (address: string, length = 6): string => {
  return `${address.substring(0, length)}...${address.substring(address.length - length)}`
}

// Data processing utilities
export const getTimeframeData = (data: any, selectedTimeframe: string) => {
  // Try new optimized structure first
  if (data.timeframes && data.timeframes[selectedTimeframe]) {
    return data.timeframes[selectedTimeframe].activity_over_time || data.activity_over_time
  }
  
  // Fallback to legacy structure
  switch (selectedTimeframe) {
    case 'daily':
      return data.daily_analytics?.activity_over_time || data.activity_over_time
    case 'monthly':
      return data.monthly_analytics?.activity_over_time || data.activity_over_time
    case 'weekly':
    default:
      return data.weekly_analytics?.activity_over_time || data.activity_over_time
  }
}

export const getCardCountData = (data: any, selectedTimeframe: string) => {
  // Try new optimized structure first
  if (data.timeframes && data.timeframes[selectedTimeframe]) {
    return data.timeframes[selectedTimeframe].slips_by_card_count || []
  }
  
  // Fallback to legacy structure
  switch (selectedTimeframe) {
    case 'daily':
      return data.daily_slips_by_card_count || []
    case 'monthly':
      return data.monthly_slips_by_card_count || []
    case 'weekly':
    default:
      return data.weekly_slips_by_card_count_new || data.weekly_slips_by_card_count || []
  }
}

// Heatmap utilities
export const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

export const buildCalendarMatrix = (
  dailyData: any[],
  valueKey: keyof any
): any[][] => {
  // Implementation for calendar heatmap matrix
  // This would be implemented based on the frontend2 logic
  return []
}

// Color scale utilities
export const blueToYellow = (t: number) => {
  const c1 = [99, 102, 241] // blue
  const c2 = [245, 158, 11] // yellow
  const rgb = c1.map((c, i) => Math.round(c + (c2[i] - c) * t))
  return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`
}

export const jerryColorScale = (t: number) => {
  if (t === 0) return '#f3f4f6'
  if (t < 0.1) return '#dbeafe'
  if (t < 0.3) return '#93c5fd'
  if (t < 0.6) return '#3b82f6'
  if (t < 0.8) return '#1d4ed8'
  return '#1e40af'
}

export const getHeatmapColor = (value: number, maxValue: number, colorType: "blue-yellow" | "green-red" = "blue-yellow"): string => {
  if (maxValue === 0) return '#f3f4f6'
  const ratio = value / maxValue
  
  if (colorType === "green-red") {
    // Green to red scale
    if (ratio === 0) return '#f3f4f6'
    if (ratio < 0.1) return '#dcfce7'
    if (ratio < 0.3) return '#86efac'
    if (ratio < 0.6) return '#22c55e'
    if (ratio < 0.8) return '#15803d'
    return '#166534'
  }
  
  // Default blue-yellow scale
  return jerryColorScale(ratio)
}
