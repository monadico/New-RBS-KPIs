// app/page.tsx
"use client"

import { useState, useEffect } from "react"
import { DashboardHeader } from "@/components/dashboard-header"
import dynamic from "next/dynamic"

// Chart Components
import { SubmissionActivityChart } from "@/components/rbs-charts/submission-activity-chart"
import { NewBettorsChart } from "@/components/rbs-charts/new-bettors-chart"
import { PlayerActivityPie } from "@/components/rbs-charts/player-activity-pie"
import { SlipsByCardStackedBar } from "@/components/rbs-charts/slips-by-card-stacked-bar"
import { OverallSlipsPie } from "@/components/rbs-charts/overall-slips-pie"
import { MonJerryVolumeArea } from "@/components/rbs-charts/mon-jerry-volume-area"
import { TotalAvgCardsChart } from "@/components/rbs-charts/total-avg-cards-chart"
import { TokenVolumeDistributionPie } from "@/components/rbs-charts/token-volume-distribution-pie"

// Claiming Chart Components
// import { ClaimingVolumeChart } from "@/components/claiming-charts/claiming-volume-chart"
// import { ClaimingTokenDistributionPie } from "@/components/claiming-charts/claiming-token-distribution-pie"
// import { ClaimingActivityTimeline } from "@/components/claiming-charts/claiming-activity-timeline"
// import { ClaimingUserActivityChart } from "@/components/claiming-charts/claiming-user-activity-chart"

// Table Components
import { RbsDailyStatsTable } from "@/components/rbs-tables/rbs-daily-stats-table"
import { RbsPeriodsTable } from "@/components/rbs-tables/rbs-periods-table"
import { CohortRetentionTable } from "@/components/rbs-tables/cohort-retention-table"
import { TopBettorsTable } from "@/components/rbs-tables/top-bettors-table"

// Auth Components
import { ProtectedComponent } from "@/components/auth/protected-component"

// Heatmap Components
import { DayOfWeekHeatmaps } from "@/components/rbs-heatmaps/day-of-week-heatmaps"
import { TraditionalHeatmap } from "@/components/rbs-heatmaps/traditional-heatmap"

import { MetricCard } from "@/components/metric-card"
import { Button } from "@/components/ui/button"
import { DollarSign, Users, CreditCard, TrendingUp } from "lucide-react"

import type { AnalyticsData } from "@/lib/data-types"
import { getTimeframeData, getCardCountData, getFilteredTimeframeData, getFilteredCardCountData, getFilteredMetrics } from "@/lib/utils"
import { EnhancedTimeframeSelector, getAvailableDateRange } from "@/components/date-range-selector"
import { ChartModal, useChartModal } from "@/components/ui/chart-modal"

export default function Page() {
  const [selectedTimeframe, setSelectedTimeframe] = useState<"daily" | "weekly" | "monthly" | "custom">("weekly")
  const [customStartDate, setCustomStartDate] = useState<Date | undefined>(undefined)
  const [customEndDate, setCustomEndDate] = useState<Date | undefined>(undefined)
  const [customRangeConfirmed, setCustomRangeConfirmed] = useState(false)
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)
  

  
  // Chart modal functionality
  const { isOpen, chartData, openModal, closeModal } = useChartModal()

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return
    
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        // Try API first, fallback to static JSON
        // Environment-based API URL
        const isProduction = process.env.NODE_ENV === 'production'
        const apiUrl = isProduction 
          ? 'https://f8s8sk80ok44gw04osco04so.173.249.24.245.sslip.io'
          : 'http://localhost:8000'
        console.log('🔍 Trying API URL:', `${apiUrl}/api/analytics`)
        
        const response = await fetch(`${apiUrl}/api/analytics`)
        console.log('📡 API Response status:', response.status)
        console.log('📡 API Response ok:', response.ok)
        
        if (!response.ok) {
          console.log('⚠️ API failed, falling back to static JSON')
          // Fallback to static JSON
          const staticResponse = await fetch('/analytics_dump.json')
          if (!staticResponse.ok) {
            throw new Error(`HTTP ${staticResponse.status}: ${staticResponse.statusText}`)
          }
          const json = await staticResponse.json()
          if (!json.success) throw new Error(json.error || 'JSON error')
          console.log('📁 Using static JSON data')
          setData(json)
        } else {
          const json = await response.json()
          console.log('✅ Using API data')
          setData(json)
        }
      } catch (err: any) {
        console.error('❌ Error loading analytics data:', err)
        // Try static JSON as fallback
        try {
          console.log('🔄 Trying static JSON fallback...')
          const staticResponse = await fetch('/analytics_dump.json')
          if (staticResponse.ok) {
            const json = await staticResponse.json()
            if (json.success) {
              console.log('📁 Using static JSON fallback data')
              setData(json)
              setLoading(false)
              return
            }
          }
        } catch (fallbackErr) {
          console.error('❌ Fallback also failed:', fallbackErr)
        }
        setError(err instanceof Error ? err.message : 'Failed to load analytics data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [mounted])

  // Handle date range changes for custom timeframe
  const handleDateRangeChange = (startDate: Date, endDate: Date) => {
    setCustomStartDate(startDate)
    setCustomEndDate(endDate)
    // The filtered data will automatically update when these state variables change
    console.log("Date range changed:", startDate, endDate)
  }

  // Handle reset to default configuration
  const handleReset = () => {
    setSelectedTimeframe("weekly")
    setCustomStartDate(undefined)
    setCustomEndDate(undefined)
    setCustomRangeConfirmed(false)
  }

  // Handle confirm custom range
  const handleConfirmCustomRange = () => {
    setCustomRangeConfirmed(true)
  }

  // Chart click handlers
  const handleSubmissionChartClick = () => {
    if (!data) return
    const timeframeData = getFilteredTimeframeData(data, selectedTimeframe, customRangeConfirmed ? customStartDate : undefined, customRangeConfirmed ? customEndDate : undefined, customRangeConfirmed)
    openModal({
      title: "Submission Activity - Detailed View",
      description: "Daily submission volume and active bettor trends over time",
      component: <SubmissionActivityChart data={timeframeData} isModal={true} />
    })
  }

  const handleVolumeChartClick = () => {
    if (!data) return
    const timeframeData = getFilteredTimeframeData(data, selectedTimeframe, customRangeConfirmed ? customStartDate : undefined, customRangeConfirmed ? customEndDate : undefined, customRangeConfirmed)
    openModal({
      title: "Token Volume Trends - Detailed View", 
      description: "$MON and $JERRY betting volume over time",
      component: <MonJerryVolumeArea data={timeframeData} isModal={true} />
    })
  }

  const handleCardCountChartClick = () => {
    if (!data) return
    const cardCountData = getCardCountData(data, selectedTimeframe === "custom" ? (customRangeConfirmed ? "daily" : "weekly") : selectedTimeframe)
    openModal({
      title: "Slips by Card Count - Detailed View",
      description: "Distribution of betting slips by number of cards over time", 
      component: <SlipsByCardStackedBar data={cardCountData} isModal={true} />
    })
  }

  const handleNewBettorsChartClick = () => {
    if (!data) return
    const timeframeData = getFilteredTimeframeData(data, selectedTimeframe, customRangeConfirmed ? customStartDate : undefined, customRangeConfirmed ? customEndDate : undefined, customRangeConfirmed)
    openModal({
      title: "New Bettors Growth - Detailed View",
      description: "New and cumulative bettor acquisition over time",
      component: <NewBettorsChart data={timeframeData} isModal={true} />
    })
  }

  const handleTotalAvgCardsChartClick = () => {
    if (!data) return
    const timeframeData = getFilteredTimeframeData(data, selectedTimeframe, customRangeConfirmed ? customStartDate : undefined, customRangeConfirmed ? customEndDate : undefined, customRangeConfirmed)
    openModal({
      title: "Total & Average Cards - Detailed View",
      description: "Total cards submitted and average cards per submission over time",
      component: <TotalAvgCardsChart data={timeframeData} isModal={true} />
    })
  }

  const handleTokenVolumeDistributionClick = () => {
    if (!data) return
    const timeframeData = getFilteredTimeframeData(data, selectedTimeframe, customRangeConfirmed ? customStartDate : undefined, customRangeConfirmed ? customEndDate : undefined, customRangeConfirmed)
    openModal({
      title: "Token Volume Distribution - Detailed View",
      description: "Overall deposit volume distribution by token (MON vs JERRY)",
      component: <TokenVolumeDistributionPie data={timeframeData} isModal={true} />
    })
  }

  // Claiming Activity Click Handlers - Coming Soon
  /*
  const handleClaimingVolumeClick = () => {
    if (!data) return
    const claimingData = data.claiming_data || []
    openModal({
      title: "Claiming Volume - Detailed View",
      description: "MON and JERRY claiming volumes over time",
      component: <ClaimingVolumeChart data={claimingData} isModal={true} />
    })
  }

  const handleClaimingTokenDistributionClick = () => {
    if (!data) return
    const claimingData = data.claiming_data || []
    openModal({
      title: "Claiming Token Distribution - Detailed View",
      description: "Distribution of MON vs JERRY claiming transactions",
      component: <ClaimingTokenDistributionPie data={claimingData} isModal={true} />
    })
  }

  const handleClaimingActivityClick = () => {
    if (!data) return
    const claimingData = data.claiming_data || []
    openModal({
      title: "Claiming Activity Timeline - Detailed View",
      description: "Timeline of claiming activity and patterns",
      component: <ClaimingActivityTimeline data={claimingData} isModal={true} />
    })
  }

  const handleClaimingUserActivityClick = () => {
    if (!data) return
    const claimingData = data.claiming_data || []
    openModal({
      title: "Claiming User Activity - Detailed View",
      description: "User activity patterns in claiming transactions",
      component: <ClaimingUserActivityChart data={claimingData} isModal={true} />
    })
  }
  */
  
  // Calculate active users based on selected timeframe
  const getActiveUsersForTimeframe = () => {
    if (!data) return 0
    
    if (selectedTimeframe === "custom" && customRangeConfirmed && customStartDate && customEndDate) {
      // Use filtered data for custom timeframe
      const filteredData = getFilteredTimeframeData(data, selectedTimeframe, customStartDate, customEndDate, customRangeConfirmed)
      return filteredData.length > 0 ? filteredData[filteredData.length - 1].active_addresses : 0
    } else if (selectedTimeframe === "custom" && !customRangeConfirmed) {
      // Use weekly data when custom is selected but not confirmed
      const timeframeData = data.timeframes?.weekly?.activity_over_time || []
      return timeframeData.length > 0 ? timeframeData[timeframeData.length - 1].active_addresses : 0
    } else {
      // Use regular timeframe data
      const timeframeData = data.timeframes?.[selectedTimeframe]?.activity_over_time || []
      return timeframeData.length > 0 ? timeframeData[timeframeData.length - 1].active_addresses : 0
    }
  }

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return null
  }

  if (loading) {
    return (
      <div className="flex min-h-screen bg-bg-base items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-accent-primary"></div>
        <p className="ml-4 text-text-primary">Loading dashboard data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen bg-bg-base items-center justify-center flex-col">
        <p className="text-rbs-red text-lg mb-4">{error}</p>
        <Button onClick={() => window.location.reload()} className="bg-rbs-blue text-white">
          Retry
        </Button>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="flex min-h-screen bg-bg-base items-center justify-center text-text-secondary">
        No data available.
      </div>
    )
  }

  // Get timeframe-specific data
  const timeframeData = getFilteredTimeframeData(data, selectedTimeframe, customRangeConfirmed ? customStartDate : undefined, customRangeConfirmed ? customEndDate : undefined, customRangeConfirmed)
  const cardCountData = getCardCountData(data, selectedTimeframe === "custom" ? (customRangeConfirmed ? "daily" : "weekly") : selectedTimeframe)
  const availableDateRange = getAvailableDateRange(data)
  
  // Get claiming data (placeholder for now)
  const claimingData = data.claiming_data || []

  // Debug logging
  console.log("Available date range:", availableDateRange)
  console.log("Custom start date:", customStartDate)
  console.log("Custom end date:", customEndDate)
  console.log("Custom range confirmed:", customRangeConfirmed)
  console.log("Selected timeframe:", selectedTimeframe)
  console.log("Timeframe data length:", timeframeData?.length)

  // Get filtered metrics for custom timeframe
  const filteredMetrics = getFilteredMetrics(data, selectedTimeframe, customRangeConfirmed ? customStartDate : undefined, customRangeConfirmed ? customEndDate : undefined, customRangeConfirmed)

  const {
    total_metrics,
    average_metrics,
    activity_over_time,
    player_activity,
    overall_slips_by_card_count,
    top_bettors,
    rbs_stats_by_periods,
    cohort_retention,
  } = data

  return (
    <div className="min-h-screen bg-bg-base">
      <DashboardHeader />
      <main className="container mx-auto px-6 py-8 space-y-8">
        {/* Main Title and Subtitle */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-text-primary tracking-tight mb-2">RBS Analytics Dashboard</h1>
          <p className="text-text-secondary text-base leading-relaxed max-w-2xl mx-auto">
            Check out the latest metrics of your favorite sports betting app!
          </p>
        </div>

        {/* Enhanced Timeframe Selector with Custom Date Range */}
        <EnhancedTimeframeSelector 
          selectedTimeframe={selectedTimeframe} 
          onSelectTimeframe={setSelectedTimeframe}
          startDate={customStartDate}
          endDate={customEndDate}
          onDateRangeChange={handleDateRangeChange}
          availableDateRange={availableDateRange || undefined}
          onReset={handleReset}
          onConfirmCustomRange={handleConfirmCustomRange}
          customRangeConfirmed={customRangeConfirmed}
        />

        {/* Metrics Section - Row 1: Primary Metrics */}
        <section id="overview" className="animate-fade-in-up">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <MetricCard
              title="Total Submissions"
              value={filteredMetrics.total_submissions}
              format="number"
              accentColor="text-rbs-lime"
              icon={<TrendingUp className="w-5 h-5 text-rbs-accent" />}
            />
            <MetricCard
              title="Active Bettors"
              value={filteredMetrics.total_active_addresses}
              format="number"
              accentColor="text-rbs-lime"
              icon={<Users className="w-5 h-5 text-rbs-over" />}
            />
            <MetricCard
              title="$MON Volume"
              value={filteredMetrics.total_mon_volume}
              format="currency"
              accentColor="text-rbs-lime"
              icon={<DollarSign className="w-5 h-5 text-rbs-focused" />}
            />
            <MetricCard
              title="$JERRY Volume"
              value={filteredMetrics.total_jerry_volume}
              format="currency"
              accentColor="text-rbs-lime"
              icon={<DollarSign className="w-5 h-5 text-rbs-boxing" />}
            />
          </div>
        </section>



        {/* Metrics Section - Row 2: Averages */}
        <section className="animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              title="Avg Submissions per Day"
              value={filteredMetrics.avg_submissions_per_day}
              format="number"
              accentColor="text-rbs-lime"
              icon={<TrendingUp className="w-5 h-5 text-rbs-accent" />}
            />
            <MetricCard
              title={selectedTimeframe === "daily" ? "Daily Active Users" : selectedTimeframe === "weekly" ? "Weekly Active Users" : selectedTimeframe === "monthly" ? "Monthly Active Users" : selectedTimeframe === "custom" && customRangeConfirmed ? "Custom Range Active Users" : "Weekly Active Users"}
              value={getActiveUsersForTimeframe()}
              format="number"
              accentColor="text-rbs-lime"
              icon={<Users className="w-5 h-5 text-rbs-over" />}
            />
            <MetricCard
              title="Avg Cards per RareLink Slip"
              value={filteredMetrics.avg_cards_per_slip}
              format="decimal"
              accentColor="text-rbs-lime"
              icon={<CreditCard className="w-5 h-5 text-rbs-focused" />}
            />
          </div>
        </section>

        {/* Charts Section - Row 1: Three Large Charts */}
        <section
          id="submissions"
          className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-delayed"
          style={{ animationDelay: "0.7s" }}
        >
          <SubmissionActivityChart data={timeframeData} onChartClick={handleSubmissionChartClick} />
          <NewBettorsChart data={timeframeData} onChartClick={handleNewBettorsChartClick} />
          <MonJerryVolumeArea data={timeframeData} onChartClick={handleVolumeChartClick} />
        </section>

        {/* Claiming Metrics Section */}
        <section
          id="claiming-metrics"
          className="animate-fade-in-delayed"
          style={{ animationDelay: "0.75s" }}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              title="Total Claimer Addresses"
              value={0}
              format="number"
              accentColor="text-rbs-lime"
              icon={<Users className="w-5 h-5 text-rbs-over" />}
            />
            <MetricCard
              title="Total MON Claimed"
              value={data.total_metrics?.total_mon_volume || 0}
              format="currency"
              accentColor="text-rbs-lime"
              icon={<DollarSign className="w-5 h-5 text-rbs-under" />}
            />
            <MetricCard
              title="Total JERRY Claimed"
              value={data.total_metrics?.total_jerry_volume || 0}
              format="currency"
              accentColor="text-rbs-lime"
              icon={<DollarSign className="w-5 h-5 text-rbs-focused" />}
            />
          </div>
        </section>

        {/* Claiming Activity Section - Coming Soon */}
        {/* <section
          id="claiming"
          className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-delayed"
          style={{ animationDelay: "0.8s" }}
        >
          <div className="lg:col-span-1">
            <div className="h-full flex flex-col space-y-6">
              <div className="flex-1">
                <ClaimingVolumeChart data={claimingData} onChartClick={handleClaimingVolumeClick} />
              </div>
              <div className="flex-1">
                <ClaimingTokenDistributionPie data={claimingData} onChartClick={handleClaimingTokenDistributionClick} />
              </div>
            </div>
          </div>
          <div className="lg:col-span-2">
            <div className="h-full flex flex-col space-y-6">
              <div className="flex-1">
                <ClaimingActivityTimeline data={claimingData} onChartClick={handleClaimingActivityClick} />
              </div>
              <div className="flex-1">
                <ClaimingUserActivityChart data={claimingData} onChartClick={handleClaimingUserActivityClick} />
              </div>
            </div>
          </div>
        </section> */}

        {/* Charts Section - Row 2: Three Charts (Balanced Layout) */}
        <section
          id="players"
          className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-delayed"
          style={{ animationDelay: "0.9s" }}
        >
          <div className="lg:col-span-1">
            <div className="h-full flex flex-col space-y-6">
              <div className="flex-1">
                <PlayerActivityPie data={player_activity.categories} totalPlayers={player_activity.total_players} />
              </div>
              <div className="flex-1">
                <OverallSlipsPie data={overall_slips_by_card_count} />
              </div>
              <div className="flex-1">
                <TokenVolumeDistributionPie data={timeframeData} onChartClick={handleTokenVolumeDistributionClick} />
              </div>
            </div>
          </div>
          <div className="lg:col-span-2">
            <div className="h-full flex flex-col space-y-6">
              <div className="flex-1">
            <SlipsByCardStackedBar data={cardCountData} onChartClick={handleCardCountChartClick} />
          </div>
              <div className="flex-1">
                <TotalAvgCardsChart data={timeframeData} onChartClick={handleTotalAvgCardsChartClick} />
              </div>
            </div>
          </div>
        </section>

        {/* Tables Section */}
        <section className="animate-fade-in-delayed" style={{ animationDelay: "1.5s" }}>
          <div className="mb-8">
            <ProtectedComponent 
              title="Daily Statistics" 
              description="Login to view detailed daily analytics and performance metrics"
            >
              <RbsDailyStatsTable data={data.timeframes?.daily?.activity_over_time || data.activity_over_time || []} />
            </ProtectedComponent>
          </div>
          {rbs_stats_by_periods && rbs_stats_by_periods.length > 0 && (
            <div className="mb-8">
              <ProtectedComponent 
                title="RBS Stats by Periods" 
                description="Login to view aggregated performance metrics for different time periods"
              >
                <RbsPeriodsTable data={rbs_stats_by_periods} />
              </ProtectedComponent>
            </div>
          )}
          {cohort_retention && cohort_retention.length > 0 && (
            <div className="mb-8">
              <ProtectedComponent 
                title="Cohort Retention Analysis" 
                description="Login to view weekly user retention patterns and engagement metrics"
              >
                <CohortRetentionTable data={cohort_retention} />
              </ProtectedComponent>
            </div>
          )}
          <TopBettorsTable data={top_bettors} />
        </section>

        {/* Heatmaps Section */}
        <section className="animate-fade-in-delayed" style={{ animationDelay: "1.6s" }}>
          <div className="space-y-8">
            <ProtectedComponent 
              title="Activity Heatmap" 
              description="Login to view detailed activity patterns and heatmap analytics"
            >
              <TraditionalHeatmap data={data.timeframes?.daily?.activity_over_time || []} />
            </ProtectedComponent>
            <ProtectedComponent 
              title="Day of Week Heatmaps" 
              description="Login to view day-of-week activity patterns and trends"
            >
              <DayOfWeekHeatmaps data={data.timeframes?.daily?.activity_over_time || []} />
            </ProtectedComponent>
          </div>
        </section>
      </main>

      {/* Chart Modal */}
      <ChartModal
        isOpen={isOpen}
        onClose={closeModal}
        title={chartData?.title || ""}
        description={chartData?.description}
      >
        {chartData?.component}
      </ChartModal>
    </div>
  )
}
