"use client"

import * as React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { format, startOfMonth, endOfMonth, eachDayOfInterval, startOfWeek, endOfWeek, isSameMonth, isSameDay, isToday } from "date-fns"
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"

export interface CalendarProps {
  mode?: "single" | "multiple" | "range"
  selected?: Date | Date[] | { from: Date; to?: Date }
  onSelect?: (date: Date | undefined) => void
  disabled?: (date: Date) => boolean
  className?: string
  showOutsideDays?: boolean
  initialFocus?: boolean
}

function Calendar({
  mode = "single",
  selected,
  onSelect,
  disabled,
  className,
  showOutsideDays = true,
  initialFocus = false,
}: CalendarProps) {
  const [currentMonth, setCurrentMonth] = React.useState(new Date())

  const monthStart = startOfMonth(currentMonth)
  const monthEnd = endOfMonth(currentMonth)
  const calendarStart = startOfWeek(monthStart)
  const calendarEnd = endOfWeek(monthEnd)

  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd })

  const isSelected = (date: Date) => {
    if (!selected) return false
    if (mode === "single" && selected instanceof Date) {
      return isSameDay(date, selected)
    }
    return false
  }

  const isDisabled = (date: Date) => {
    if (disabled) return disabled(date)
    return false
  }

  const handleDateClick = (date: Date) => {
    if (isDisabled(date)) return
    onSelect?.(date)
  }

  const goToPreviousMonth = () => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev)
      newMonth.setMonth(prev.getMonth() - 1)
      return newMonth
    })
  }

  const goToNextMonth = () => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev)
      newMonth.setMonth(prev.getMonth() + 1)
      return newMonth
    })
  }

  return (
    <div className={cn("p-3", className)}>
      {/* Header */}
      <div className="flex justify-center pt-1 relative items-center mb-4">
        <button
          onClick={goToPreviousMonth}
          className={cn(
            buttonVariants({ variant: "outline" }),
            "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100 absolute left-1"
          )}
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <div className="text-sm font-medium">
          {format(currentMonth, "MMMM yyyy")}
        </div>
        <button
          onClick={goToNextMonth}
          className={cn(
            buttonVariants({ variant: "outline" }),
            "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100 absolute right-1"
          )}
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      {/* Day Headers */}
      <div className="grid grid-cols-7 gap-0 w-full mb-2">
        {["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map((day) => (
          <div
            key={day}
            className="text-muted-foreground rounded-md w-9 font-normal text-[0.8rem] text-center p-0 m-0"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="space-y-1">
        {Array.from({ length: Math.ceil(days.length / 7) }, (_, weekIndex) => (
          <div key={weekIndex} className="grid grid-cols-7 gap-0 w-full">
            {days.slice(weekIndex * 7, (weekIndex + 1) * 7).map((day) => {
              const isOutsideMonth = !isSameMonth(day, currentMonth)
              const isSelectedDay = isSelected(day)
              const isTodayDay = isToday(day)
              const isDisabledDay = isDisabled(day)

              if (!showOutsideDays && isOutsideMonth) {
                return <div key={day.toString()} className="h-9 w-9" />
              }

              return (
                <div
                  key={day.toString()}
                  className={cn(
                    "h-9 w-9 text-center text-sm p-0 relative",
                    isSelectedDay && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground",
                    isTodayDay && !isSelectedDay && "bg-accent text-accent-foreground",
                    isOutsideMonth && "text-muted-foreground opacity-50",
                    isDisabledDay && "text-muted-foreground opacity-50 cursor-not-allowed",
                    !isDisabledDay && !isOutsideMonth && "hover:bg-accent hover:text-accent-foreground cursor-pointer"
                  )}
                  onClick={() => handleDateClick(day)}
                >
                  <div className="h-9 w-9 flex items-center justify-center">
                    {format(day, "d")}
                  </div>
                </div>
              )
            })}
          </div>
        ))}
      </div>
    </div>
  )
}

Calendar.displayName = "Calendar"

export { Calendar }
