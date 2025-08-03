// components/date-range-selector.tsx
"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { Calendar as CalendarIcon, ChevronDown, RotateCcw } from "lucide-react"
import { format, parseISO, isValid } from "date-fns"

interface DateRangeSelectorProps {
  startDate: Date
  endDate: Date
  onStartDateChange: (date: Date) => void
  onEndDateChange: (date: Date) => void
  minDate?: Date
  maxDate?: Date
  className?: string
}

export function DateRangeSelector({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  minDate,
  maxDate,
  className
}: DateRangeSelectorProps) {
  const [startCalendarOpen, setStartCalendarOpen] = useState(false)
  const [endCalendarOpen, setEndCalendarOpen] = useState(false)

  // Set minimum start date to 2025-02-03
  const effectiveMinDate = new Date("2025-02-03")
  
  // Use the provided maxDate (from API data) or fallback to current date
  const effectiveMaxDate = maxDate || new Date()

  // Debug logging
  console.log("DateRangeSelector - maxDate:", maxDate)
  console.log("DateRangeSelector - effectiveMaxDate:", effectiveMaxDate)
  console.log("DateRangeSelector - startDate:", startDate)
  console.log("DateRangeSelector - endDate:", endDate)

  const handleReset = () => {
    // Reset to default dates
    const defaultStart = new Date("2025-02-04")
    const defaultEnd = effectiveMaxDate
    
    onStartDateChange(defaultStart)
    onEndDateChange(defaultEnd)
  }

  const isDateRangeValid = startDate <= endDate

  return (
    <div className={cn("flex flex-col sm:flex-row items-center gap-4", className)}>
      {/* Start Date Selector */}
      <div className="flex items-center gap-2">
        <span className="text-text-secondary text-sm font-medium min-w-[80px]">Start Date:</span>
        <Popover open={startCalendarOpen} onOpenChange={setStartCalendarOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "w-[200px] justify-between bg-surface border-border-subtle",
                "hover:bg-surface-elevated hover:border-border-medium",
                "text-text-primary font-medium",
                !isDateRangeValid && "border-rbs-alert"
              )}
            >
              <div className="flex items-center gap-2">
                <CalendarIcon className="h-4 w-4 text-accent-primary" />
                {format(startDate, "MMM dd, yyyy")}
              </div>
              <ChevronDown className="h-4 w-4 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent 
            className="w-auto p-0 bg-surface border-border-medium shadow-card-elevated" 
            align="start"
          >
            <Calendar
              mode="single"
              selected={startDate}
              onSelect={(date) => {
                if (date) {
                  onStartDateChange(date)
                  setStartCalendarOpen(false)
                }
              }}
              disabled={(date) => {
                // Can't select dates before minimum start date
                if (date < effectiveMinDate) return true
                // Can't select dates after maximum end date
                if (date > effectiveMaxDate) return true
                // Can't select start date after or equal to current end date
                if (endDate && date >= endDate) return true
                return false
              }}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      {/* End Date Selector */}
      <div className="flex items-center gap-2">
        <span className="text-text-secondary text-sm font-medium min-w-[70px]">End Date:</span>
        <Popover open={endCalendarOpen} onOpenChange={setEndCalendarOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "w-[200px] justify-between bg-surface border-border-subtle",
                "hover:bg-surface-elevated hover:border-border-medium",
                "text-text-primary font-medium",
                !isDateRangeValid && "border-rbs-alert"
              )}
            >
              <div className="flex items-center gap-2">
                <CalendarIcon className="h-4 w-4 text-accent-primary" />
                {format(endDate, "MMM dd, yyyy")}
              </div>
              <ChevronDown className="h-4 w-4 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent 
            className="w-auto p-0 bg-surface border-border-medium shadow-card-elevated" 
            align="start"
          >
            <Calendar
              mode="single"
              selected={endDate}
              onSelect={(date) => {
                if (date) {
                  onEndDateChange(date)
                  setEndCalendarOpen(false)
                }
              }}
              disabled={(date) => {
                // Can't select dates before minimum start date
                if (date < effectiveMinDate) return true
                // Can't select dates after maximum end date
                if (date > effectiveMaxDate) return true
                // Can't select end date before or equal to current start date
                if (startDate && date <= startDate) return true
                return false
              }}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      {/* Reset Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={handleReset}
        className="bg-surface-elevated hover:bg-surface border-border-subtle"
      >
        <RotateCcw className="h-4 w-4 mr-2" />
        Reset
      </Button>

      {/* Validation Message */}
      {!isDateRangeValid && (
        <div className="text-rbs-alert text-xs font-medium">
          End date must be after start date
        </div>
      )}
    </div>
  )
}

// Enhanced timeframe selector that includes custom date range
interface EnhancedTimeframeSelectorProps {
  selectedTimeframe: "daily" | "weekly" | "monthly" | "custom"
  onSelectTimeframe: (timeframe: "daily" | "weekly" | "monthly" | "custom") => void
  startDate?: Date
  endDate?: Date
  onDateRangeChange?: (startDate: Date, endDate: Date) => void
  availableDateRange?: { min: Date; max: Date }
  className?: string
  onReset?: () => void
  customRangeConfirmed?: boolean
  onConfirmCustomRange?: () => void
}

export function EnhancedTimeframeSelector({
  selectedTimeframe,
  onSelectTimeframe,
  startDate,
  endDate,
  onDateRangeChange,
  availableDateRange,
  className,
  onReset,
  customRangeConfirmed,
  onConfirmCustomRange
}: EnhancedTimeframeSelectorProps) {
  // Set default dates based on available range
  const defaultStartDate = availableDateRange?.min || new Date("2025-02-04")
  const defaultEndDate = availableDateRange?.max || new Date()
  
  // Debug logging
  console.log("EnhancedTimeframeSelector - availableDateRange:", availableDateRange)
  console.log("EnhancedTimeframeSelector - defaultStartDate:", defaultStartDate)
  console.log("EnhancedTimeframeSelector - defaultEndDate:", defaultEndDate)
  
  const [localStartDate, setLocalStartDate] = useState(startDate || defaultStartDate)
  const [localEndDate, setLocalEndDate] = useState(endDate || defaultEndDate)
  const [rangeModified, setRangeModified] = useState(false)

  useEffect(() => {
    if (startDate) setLocalStartDate(startDate)
    if (endDate) setLocalEndDate(endDate)
  }, [startDate, endDate])

  // Reset rangeModified when customRangeConfirmed changes to true
  useEffect(() => {
    if (customRangeConfirmed) {
      setRangeModified(false)
    }
  }, [customRangeConfirmed])

  // Validation for date range
  const isDateRangeValid = localStartDate <= localEndDate

  const handleDateChange = (newStartDate: Date, newEndDate: Date) => {
    setLocalStartDate(newStartDate)
    setLocalEndDate(newEndDate)
    
    // Mark range as modified if it's different from the current confirmed range
    if (customRangeConfirmed && (newStartDate !== startDate || newEndDate !== endDate)) {
      setRangeModified(true)
    }
    
    onDateRangeChange?.(newStartDate, newEndDate)
  }

  const buttonClass = (timeframe: string) =>
    cn(
      "px-6 py-3 rounded-full text-sm font-medium transition-all duration-300",
      selectedTimeframe === timeframe
        ? "bg-rbs-lime text-rbs-black shadow-glow-subtle"
        : "bg-surface-elevated text-text-secondary hover:bg-surface hover:text-text-primary border border-border-subtle",
    )

  return (
    <div className={cn("space-y-6", className)}>
      {/* Timeframe Buttons */}
      <div className="flex justify-center gap-4 animate-fade-in-up">
        <Button className={buttonClass("daily")} onClick={() => onSelectTimeframe("daily")}>
          Daily
        </Button>
        <Button className={buttonClass("weekly")} onClick={() => onSelectTimeframe("weekly")}>
          Weekly
        </Button>
        <Button className={buttonClass("monthly")} onClick={() => onSelectTimeframe("monthly")}>
          Monthly
        </Button>
        <Button className={buttonClass("custom")} onClick={() => onSelectTimeframe("custom")}>
          Custom Range
        </Button>
      </div>

      {/* Date Range Selector - Only shown when custom is selected */}
      {selectedTimeframe === "custom" && (
        <div className="flex flex-col items-center gap-4 animate-fade-in-up">
          <DateRangeSelector
            startDate={localStartDate}
            endDate={localEndDate}
            onStartDateChange={(date) => handleDateChange(date, localEndDate)}
            onEndDateChange={(date) => handleDateChange(localStartDate, date)}
            minDate={availableDateRange?.min}
            maxDate={availableDateRange?.max}
            className="bg-surface-elevated p-4 rounded-lg border border-border-subtle"
          />
          
          {/* Validation Message */}
          {!isDateRangeValid && (
            <div className="text-rbs-alert text-xs font-medium text-center">
              End date must be after start date
            </div>
          )}
          
          {/* Range Modified Message */}
          {rangeModified && isDateRangeValid && (
            <div className="text-amber-500 text-xs font-medium text-center">
              Date range modified - click "Update Range" to apply changes
            </div>
          )}
          
          {/* Confirm Button */}
          {((!customRangeConfirmed || rangeModified) && localStartDate && localEndDate && isDateRangeValid) && (
            <Button
              onClick={onConfirmCustomRange}
              className="bg-rbs-lime text-rbs-black hover:bg-rbs-lime/90 px-6 py-2 rounded-lg font-medium"
            >
              {rangeModified ? "Update Range" : "Confirm Range"}
            </Button>
          )}
        </div>
      )}

      {/* Reset Button - Only shown when custom is selected */}
      {selectedTimeframe === "custom" && onReset && (
        <div className="flex justify-center mt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={onReset}
            className="bg-surface-elevated hover:bg-surface border-border-subtle"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset to Weekly
          </Button>
        </div>
      )}
    </div>
  )
}

// Helper function to determine available date range from data
export function getAvailableDateRange(data: any): { min: Date; max: Date } | null {
  if (!data) return null
  
  let allDates: Date[] = []
  
  // Extract dates from different timeframe data
  const timeframes = ["daily", "weekly", "monthly"]
  timeframes.forEach(timeframe => {
    const timeframeData = data.timeframes?.[timeframe]?.activity_over_time || 
                         data[`${timeframe}_analytics`]?.activity_over_time || []
    
    timeframeData.forEach((period: any) => {
      if (period.start_date) {
        const date = parseISO(period.start_date)
        if (isValid(date)) {
          allDates.push(date)
        }
      }
    })
  })
  
  // Fallback to main activity_over_time if timeframe data not available
  if (allDates.length === 0 && data.activity_over_time) {
    data.activity_over_time.forEach((period: any) => {
      if (period.start_date) {
        const date = parseISO(period.start_date)
        if (isValid(date)) {
          allDates.push(date)
        }
      }
    })
  }
  
  if (allDates.length === 0) return null
  
  const sortedDates = allDates.sort((a, b) => a.getTime() - b.getTime())
  
  return {
    min: sortedDates[0],
    max: sortedDates[sortedDates.length - 1]
  }
} 