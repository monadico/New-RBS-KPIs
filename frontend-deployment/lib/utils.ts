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

// Filter data based on custom date range
export const filterDataByDateRange = (data: any[], startDate: Date, endDate: Date) => {
  if (!data || !Array.isArray(data)) return []
  
  // Convert dates to YYYY-MM-DD format for string comparison
  const startDateStr = startDate.toISOString().split('T')[0]
  const endDateStr = endDate.toISOString().split('T')[0]
  
  return data.filter((item) => {
    if (!item.start_date) return false
    
    // Compare dates as strings (YYYY-MM-DD format)
    const itemDateStr = item.start_date
    
    // Check if the date falls within the range (inclusive)
    return itemDateStr >= startDateStr && itemDateStr <= endDateStr
  })
}

// Get filtered timeframe data based on selection and custom date range
export const getFilteredTimeframeData = (
  data: any, 
  selectedTimeframe: string, 
  customStartDate?: Date, 
  customEndDate?: Date,
  customRangeConfirmed?: boolean
) => {
  // Get the base timeframe data
  let timeframeData = getTimeframeData(data, selectedTimeframe === "custom" ? (customRangeConfirmed ? "daily" : "weekly") : selectedTimeframe)
  
  // If custom timeframe is selected, confirmed, and we have date range, filter the data
  if (selectedTimeframe === "custom" && customRangeConfirmed && customStartDate && customEndDate) {
    timeframeData = filterDataByDateRange(timeframeData, customStartDate, customEndDate)
  }
  
  return timeframeData
}

// Get filtered card count data based on selection and custom date range
export const getFilteredCardCountData = (
  data: any, 
  selectedTimeframe: string, 
  customStartDate?: Date, 
  customEndDate?: Date
) => {
  // Get the base card count data
  let cardCountData = getCardCountData(data, selectedTimeframe === "custom" ? "daily" : selectedTimeframe)
  
  // If custom timeframe is selected and we have date range, filter the data
  if (selectedTimeframe === "custom" && customStartDate && customEndDate) {
    cardCountData = filterDataByDateRange(cardCountData, customStartDate, customEndDate)
  }
  
  return cardCountData
}

// Calculate filtered totals for metrics when custom date range is selected
export const getFilteredMetrics = (
  data: any,
  selectedTimeframe: string,
  customStartDate?: Date,
  customEndDate?: Date,
  customRangeConfirmed?: boolean
) => {
  if (selectedTimeframe !== "custom" || !customStartDate || !customEndDate || !customRangeConfirmed) {
    // Return original metrics for non-custom timeframes or unconfirmed custom
    return {
      total_submissions: data.total_metrics?.total_submissions || 0,
      total_active_addresses: data.total_metrics?.total_active_addresses || 0,
      total_mon_volume: data.total_metrics?.total_mon_volume || 0,
      total_jerry_volume: data.total_metrics?.total_jerry_volume || 0,
      avg_submissions_per_day: data.average_metrics?.avg_submissions_per_day || 0,
      avg_cards_per_slip: data.average_metrics?.avg_cards_per_slip || 0
    }
  }

  // Get filtered data for custom timeframe
  const filteredData = getFilteredTimeframeData(data, selectedTimeframe, customStartDate, customEndDate, customRangeConfirmed)
  
  if (!filteredData || filteredData.length === 0) {
    return {
      total_submissions: 0,
      total_active_addresses: 0,
      total_mon_volume: 0,
      total_jerry_volume: 0,
      avg_submissions_per_day: 0,
      avg_cards_per_slip: 0
    }
  }

  // Calculate totals from filtered data
  const totals = filteredData.reduce((acc: any, period: any) => {
    acc.total_submissions += period.submissions || 0
    acc.total_mon_volume += period.mon_volume || 0
    acc.total_jerry_volume += period.jerry_volume || 0
    return acc
  }, {
    total_submissions: 0,
    total_mon_volume: 0,
    total_jerry_volume: 0
  })

  // Calculate unique active addresses from filtered data
  const uniqueAddresses = new Set<number>()
  filteredData.forEach((period: any) => {
    if (period.active_addresses) {
      // This is a simplified approach - in reality, we'd need to track individual addresses
      // For now, we'll use the max active addresses from the filtered period
      uniqueAddresses.add(period.active_addresses)
    }
  })
  const total_active_addresses = Math.max(...Array.from(uniqueAddresses) as number[], 0)

  // Calculate averages
  const avg_submissions_per_day = filteredData.length > 0 ? totals.total_submissions / filteredData.length : 0
  const avg_cards_per_slip = data.average_metrics?.avg_cards_per_slip || 0 // Keep original for now

  return {
    total_submissions: totals.total_submissions,
    total_active_addresses,
    total_mon_volume: totals.total_mon_volume,
    total_jerry_volume: totals.total_jerry_volume,
    avg_submissions_per_day,
    avg_cards_per_slip
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
