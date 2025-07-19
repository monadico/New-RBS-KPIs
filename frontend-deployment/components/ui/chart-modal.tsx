// components/ui/chart-modal.tsx
"use client"

import React from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogOverlay, DialogPortal } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { X, Maximize2, Download } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChartModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  description?: string
  children: React.ReactNode
  className?: string
}

export function ChartModal({ 
  isOpen, 
  onClose, 
  title, 
  description, 
  children, 
  className 
}: ChartModalProps) {
  
  const handleDownload = () => {
    // In a real implementation, you would export the chart as PNG/SVG
    // For now, we'll just show a notification
    console.log("Download functionality would be implemented here")
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogPortal>
        <DialogOverlay className="bg-black/95" />
        <DialogContent 
          className={cn(
            "max-w-[95vw] w-[95vw] h-[95vh] bg-surface border-border-medium",
            "shadow-card-elevated flex flex-col",
            "data-[state=open]:animate-in data-[state=closed]:animate-out",
            "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
            "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
            "[&>button]:hidden", // Hide the default close button
            className
          )}
          style={{ backgroundColor: '#1a1a1a' }}
        >
          {/* Header */}
          <DialogHeader className="flex flex-row items-center justify-between pb-4 border-b border-border-subtle flex-shrink-0">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-accent-muted rounded-lg border border-accent-primary/20">
                <Maximize2 className="w-4 h-4 text-accent-primary" />
              </div>
              <div>
                <DialogTitle className="text-xl font-bold text-text-primary tracking-tight">
                  {title}
                </DialogTitle>
                {description && (
                  <p className="text-text-secondary text-sm mt-1">{description}</p>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownload}
                className="bg-surface-elevated hover:bg-surface border-border-subtle"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={onClose}
                className="bg-surface-elevated hover:bg-surface border-border-subtle"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </DialogHeader>

          {/* Chart Content - Takes remaining space */}
          <div className="flex-1 p-8 min-h-0">
            {/* Smaller chart container to ensure everything fits in view */}
            <div className="w-full h-full max-h-[calc(95vh-200px)] flex flex-col">
              <div className="w-full h-[450px] max-h-full">
                {children}
              </div>
            </div>
          </div>
        </DialogContent>
      </DialogPortal>
    </Dialog>
  )
}

// Hook for managing chart modal state
export function useChartModal() {
  const [isOpen, setIsOpen] = React.useState(false)
  const [chartData, setChartData] = React.useState<{
    title: string
    description?: string
    component: React.ReactNode
  } | null>(null)

  const openModal = (data: {
    title: string
    description?: string
    component: React.ReactNode
  }) => {
    setChartData(data)
    setIsOpen(true)
  }

  const closeModal = () => {
    setIsOpen(false)
    // Clear data after animation completes
    setTimeout(() => setChartData(null), 200)
  }

  return {
    isOpen,
    chartData,
    openModal,
    closeModal,
  }
}

// Wrapper component for making charts clickable
interface ClickableChartProps {
  title: string
  description?: string
  children: React.ReactNode
  enlargedComponent?: React.ReactNode
  onChartClick?: () => void
  className?: string
}

export function ClickableChart({ 
  title, 
  description, 
  children, 
  enlargedComponent,
  onChartClick,
  className 
}: ClickableChartProps) {
  const handleClick = () => {
    if (onChartClick) {
      onChartClick()
    }
  }

  return (
    <div 
      className={cn(
        "cursor-pointer transition-all duration-200 group",
        "hover:scale-[1.02] hover:shadow-glow-medium",
        "relative overflow-hidden",
        className
      )}
      onClick={handleClick}
    >
      {/* Hover overlay */}
      <div className="absolute inset-0 bg-accent-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10" />
      
      {/* Expand icon overlay */}
      <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <div className="p-2 bg-bg-elevated/90 backdrop-blur-sm rounded-lg border border-border-subtle">
          <Maximize2 className="w-4 h-4 text-accent-primary" />
        </div>
      </div>
      
      {children}
    </div>
  )
} 