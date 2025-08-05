// components/date-range-selector.tsx
"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { Calendar as CalendarIcon, ChevronDown, RotateCcw, Loader2 } from "lucide-react"
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

  const isDateRangeValid = startDate <= endDate

  return (
    <div className={cn("flex flex-col lg:flex-row items-center justify-center gap-4 lg:gap-6", className)}>
      {/* Start Date Selector */}
      <div className="flex flex-col sm:flex-row items-center gap-2 w-full sm:w-auto">
        <span className="text-text-secondary text-sm font-medium min-w-[80px] text-center sm:text-left">Start Date:</span>
        <Popover open={startCalendarOpen} onOpenChange={setStartCalendarOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "w-full sm:w-[200px] justify-between bg-surface border-border-subtle h-12 sm:h-auto",
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
      <div className="flex flex-col sm:flex-row items-center gap-2 w-full sm:w-auto">
        <span className="text-text-secondary text-sm font-medium min-w-[80px] text-center sm:text-left">End Date:</span>
        <Popover open={endCalendarOpen} onOpenChange={setEndCalendarOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "w-full sm:w-[200px] justify-between bg-surface border-border-subtle h-12 sm:h-auto",
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
    </div>
  )
}

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
  customRangeLoading?: boolean
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
  onConfirmCustomRange,
  customRangeLoading
}: EnhancedTimeframeSelectorProps) {
  const [localStartDate, setLocalStartDate] = useState<Date>(startDate || new Date())
  const [localEndDate, setLocalEndDate] = useState<Date>(endDate || new Date())
  const [rangeModified, setRangeModified] = useState(false)
  const [isTransitioning, setIsTransitioning] = useState(false)

  // Update local dates when props change
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

  const handleTimeframeSelect = (timeframe: "daily" | "weekly" | "monthly" | "custom") => {
    if (timeframe === "custom") {
      setIsTransitioning(true)
      // Simulate a brief loading state for better UX
      setTimeout(() => {
        setIsTransitioning(false)
        onSelectTimeframe(timeframe)
      }, 300)
    } else {
      onSelectTimeframe(timeframe)
    }
  }

  const buttonClass = (timeframe: string) =>
    cn(
      "px-6 py-3 rounded-full text-sm font-medium transition-all duration-300",
      selectedTimeframe === timeframe
        ? "bg-rbs-lime text-rbs-black shadow-glow-subtle"
        : "bg-surface-elevated text-text-secondary hover:bg-surface hover:text-text-primary border border-border-subtle",
    )

  return (
    <div className={cn("space-y-4 sm:space-y-6", className)}>
      {/* Timeframe Buttons - Enhanced Desktop Layout */}
      <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4 lg:gap-6 animate-fade-in-up">
        <Button 
          className={cn(
            buttonClass("daily"),
            "h-12 sm:h-auto px-6 py-3 sm:py-3 lg:px-8 lg:py-4 text-base sm:text-sm lg:text-base font-medium"
          )} 
          onClick={() => handleTimeframeSelect("daily")}
        >
          Daily
        </Button>
        <Button 
          className={cn(
            buttonClass("weekly"),
            "h-12 sm:h-auto px-6 py-3 sm:py-3 lg:px-8 lg:py-4 text-base sm:text-sm lg:text-base font-medium"
          )} 
          onClick={() => handleTimeframeSelect("weekly")}
        >
          Weekly
        </Button>
        <Button 
          className={cn(
            buttonClass("monthly"),
            "h-12 sm:h-auto px-6 py-3 sm:py-3 lg:px-8 lg:py-4 text-base sm:text-sm lg:text-base font-medium"
          )} 
          onClick={() => handleTimeframeSelect("monthly")}
        >
          Monthly
        </Button>
        <Button 
          className={cn(
            buttonClass("custom"),
            "h-12 sm:h-auto px-6 py-3 sm:py-3 lg:px-8 lg:py-4 text-base sm:text-sm lg:text-base font-medium"
          )} 
          onClick={() => handleTimeframeSelect("custom")}
        >
          Custom Range
        </Button>
      </div>

      {/* Date Range Selector - Enhanced Desktop Layout */}
      {selectedTimeframe === "custom" && (
        <div className="flex flex-col items-center gap-4 lg:gap-6 animate-fade-in-up">
          {/* Loading State */}
          {isTransitioning && (
            <div className="flex items-center justify-center p-8">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="h-8 w-8 animate-spin text-rbs-lime" />
                <p className="text-text-secondary text-sm font-medium">Loading custom range...</p>
              </div>
            </div>
          )}

          {/* Date Range Content - Enhanced Desktop Layout */}
          {!isTransitioning && (
            <>
              {/* Centered Date Range Container */}
              <div className="w-full max-w-2xl lg:max-w-4xl flex justify-center">
                <div className="bg-surface-elevated p-4 lg:p-6 rounded-lg border border-border-subtle w-full max-w-2xl">
                  <DateRangeSelector
                    startDate={localStartDate}
                    endDate={localEndDate}
                    onStartDateChange={(date) => handleDateChange(date, localEndDate)}
                    onEndDateChange={(date) => handleDateChange(localStartDate, date)}
                    minDate={availableDateRange?.min}
                    maxDate={availableDateRange?.max}
                    className="w-full"
                  />
                </div>
              </div>
              
              {/* Validation Message */}
              {!isDateRangeValid && (
                <div className="text-rbs-alert text-xs lg:text-sm font-medium text-center">
                  End date must be after start date
                </div>
              )}
              
              {/* Range Modified Message */}
              {rangeModified && isDateRangeValid && (
                <div className="text-amber-500 text-xs lg:text-sm font-medium text-center">
                  Date range modified - click "Update Range" to apply changes
                </div>
              )}
              
              {/* Centered Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 lg:gap-4 justify-center items-center w-full max-w-2xl">
                {/* Confirm Button */}
                {((!customRangeConfirmed || rangeModified) && localStartDate && localEndDate && isDateRangeValid) && (
                  <Button
                    onClick={onConfirmCustomRange}
                    disabled={customRangeLoading}
                    className="bg-rbs-lime text-rbs-black hover:bg-rbs-lime/90 px-6 py-3 lg:px-8 lg:py-4 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed h-12 sm:h-auto lg:text-base min-w-[140px]"
                  >
                    {customRangeLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Querying...
                      </>
                    ) : (
                      rangeModified ? "Update Range" : "Confirm Range"
                    )}
                  </Button>
                )}
                
                {/* Reset Button */}
                {onReset && (
                  <Button
                    onClick={onReset}
                    variant="outline"
                    className="border-border-subtle text-text-secondary hover:bg-surface hover:text-text-primary h-12 sm:h-auto lg:px-8 lg:py-4 lg:text-base min-w-[120px]"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reset
                  </Button>
                )}
              </div>
            </>
          )}
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