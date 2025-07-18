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

// Table Components
import { RbsStatsTable } from "@/components/rbs-tables/rbs-stats-table"
import { TopBettorsTable } from "@/components/rbs-tables/top-bettors-table"

// Heatmap Components
import { DayOfWeekHeatmaps } from "@/components/rbs-heatmaps/day-of-week-heatmaps"
import { TraditionalHeatmap } from "@/components/rbs-heatmaps/traditional-heatmap"

import { MetricCard } from "@/components/metric-card"
import { Button } from "@/components/ui/button"
import { DollarSign, Users, CreditCard, TrendingUp } from "lucide-react"

import type { AnalyticsData } from "@/lib/data-types"
import { getTimeframeData, getCardCountData } from "@/lib/utils"
import { TimeframeSelector } from "@/components/timeframe-selector"

export default function Page() {
  const [selectedTimeframe, setSelectedTimeframe] = useState<"daily" | "weekly" | "monthly">("weekly")
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

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
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://173.249.24.245:8000'
        const response = await fetch(`${apiUrl}/api/analytics`)
        if (!response.ok) {
          // Fallback to static JSON
          const staticResponse = await fetch('/analytics_dump.json')
          if (!staticResponse.ok) {
            throw new Error(`HTTP ${staticResponse.status}: ${staticResponse.statusText}`)
          }
          const json = await staticResponse.json()
          if (!json.success) throw new Error(json.error || 'JSON error')
          setData(json)
        } else {
          const json = await response.json()
          setData(json)
        }
      } catch (err: any) {
        console.error('Error loading analytics data:', err)
        // Try static JSON as fallback
        try {
          const staticResponse = await fetch('/analytics_dump.json')
          if (staticResponse.ok) {
            const json = await staticResponse.json()
            if (json.success) {
              setData(json)
              setLoading(false)
              return
            }
          }
        } catch (fallbackErr) {
          console.error('Fallback also failed:', fallbackErr)
        }
        setError(err instanceof Error ? err.message : 'Failed to load analytics data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [mounted])

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
  const timeframeData = getTimeframeData(data, selectedTimeframe)
  const cardCountData = getCardCountData(data, selectedTimeframe)

  const {
    total_metrics,
    average_metrics,
    activity_over_time,
    player_activity,
    overall_slips_by_card_count,
    top_bettors,
    rbs_stats_by_periods,
  } = data

  return (
    <div className="min-h-screen bg-bg-base">
      <DashboardHeader />
      <main className="container mx-auto px-6 py-8 space-y-8">
        {/* Main Title and Subtitle */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-text-primary tracking-tight mb-2">📊 RBS Analytics Dashboard</h1>
          <p className="text-text-secondary text-base leading-relaxed max-w-2xl mx-auto">
            Real-time insights into RareBetSports ecosystem performance
          </p>
        </div>

        {/* Timeframe Selector */}
        <TimeframeSelector selectedTimeframe={selectedTimeframe} onSelectTimeframe={setSelectedTimeframe} />

        {/* Metrics Section - Row 1: Primary Metrics */}
        <section id="overview" className="animate-fade-in-up">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total RareLink Submissions"
              value={total_metrics.total_submissions}
              format="number"
              accentColor="text-rbs-lime"
              icon={<TrendingUp className="w-5 h-5 text-rbs-accent" />}
            />
            <MetricCard
              title="Total Active Addresses"
              value={total_metrics.total_active_addresses}
              format="number"
              accentColor="text-rbs-lime"
              icon={<Users className="w-5 h-5 text-rbs-over" />}
            />
            <MetricCard
              title="Total $MON Volume"
              value={total_metrics.total_mon_volume}
              format="currency"
              accentColor="text-rbs-lime"
              icon={<DollarSign className="w-5 h-5 text-rbs-under" />}
            />
            <MetricCard
              title="Total $JERRY Volume"
              value={total_metrics.total_jerry_volume}
              format="currency"
              accentColor="text-rbs-lime"
              icon={<DollarSign className="w-5 h-5 text-rbs-focused" />}
            />
          </div>
        </section>

        {/* Metrics Section - Row 2: Average Metrics */}
        <section className="animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              title="Avg Submissions per Day"
              value={average_metrics.avg_submissions_per_day}
              format="number"
              accentColor="text-rbs-lime"
              icon={<TrendingUp className="w-5 h-5 text-rbs-accent" />}
            />
            <MetricCard
              title="Avg Players per Day"
              value={average_metrics.avg_players_per_day}
              format="number"
              accentColor="text-rbs-lime"
              icon={<Users className="w-5 h-5 text-rbs-over" />}
            />
            <MetricCard
              title="Avg Cards per RareLink Slip"
              value={average_metrics.avg_cards_per_slip}
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
          <SubmissionActivityChart data={timeframeData} />
          <NewBettorsChart data={timeframeData} />
          <MonJerryVolumeArea data={timeframeData} />
        </section>

        {/* Charts Section - Row 2: Three Charts (Balanced Layout) */}
        <section
          id="players"
          className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-delayed"
          style={{ animationDelay: "0.9s" }}
        >
          <div className="lg:col-span-1">
            <div className="space-y-6">
            <PlayerActivityPie data={player_activity.categories} totalPlayers={player_activity.total_players} />
              <OverallSlipsPie data={overall_slips_by_card_count} />
            </div>
          </div>
          <div className="lg:col-span-2">
            <div className="h-full flex flex-col space-y-6">
              <div className="flex-1">
            <SlipsByCardStackedBar data={cardCountData} />
          </div>
              <div className="flex-1">
                <TotalAvgCardsChart data={timeframeData} />
              </div>
            </div>
          </div>
        </section>



        {/* Tables Section */}
        <section className="animate-fade-in-delayed" style={{ animationDelay: "1.5s" }}>
          {rbs_stats_by_periods && rbs_stats_by_periods.length > 0 && (
            <div className="mb-8">
              <RbsStatsTable data={rbs_stats_by_periods} />
            </div>
          )}
          <TopBettorsTable data={top_bettors} />
        </section>

        {/* Heatmaps Section */}
        <section className="animate-fade-in-delayed" style={{ animationDelay: "1.6s" }}>
          <div className="space-y-8">
            <TraditionalHeatmap data={data.timeframes?.daily?.activity_over_time || []} />
          <DayOfWeekHeatmaps data={data.timeframes?.daily?.activity_over_time || []} />
          </div>
        </section>
      </main>
    </div>
  )
}
