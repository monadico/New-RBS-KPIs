// lib/data-types.ts
export interface PeriodData {
  period: number
  start_date: string
  end_date: string
  submissions: number
  active_addresses: number
  new_bettors: number
  mon_volume: number
  jerry_volume: number
  total_volume: number
  total_cards: number
  avg_cards_per_submission: number
  avg_bet_amount?: number
  mon_transactions?: number
  jerry_transactions?: number
}

export interface PlayerCategory {
  category: string
  player_count: number
  percentage: number
}

export interface SlipCardCount {
  cards_in_slip: number
  bets: number
  percentage: number
}

export interface TopBettor {
  user_address: string
  rank: number
  total_mon: number
  total_jerry: number
  total_bets: number
  avg_cards_per_slip: number
  active_days: number
}

export interface TopClaimer {
  address: string
  display_address: string
  rank: number
  total_claimed: number
  mon_claimed: number
  jerry_claimed: number
  total_claims: number
  avg_claim_amount: number
  mon_percentage: number
  jerry_percentage: number
  mon_bet: number
  jerry_bet: number
  total_bet: number
  profit_percentage: number
  total_submissions: number
  avg_slip_size: number
}

export interface RbsStatsPeriod {
  period: string
  mon_volume: number
  jerry_volume: number
  total_volume: number
  submissions: number
  active_bettors: number
  total_cards: number
}

export interface CohortRetentionWeek {
  users: number
  percentage: number
}

export interface CohortRetentionData {
  earliest_date: string
  users: number
  retention_weeks: {
    [key: string]: CohortRetentionWeek
  }
}

export interface CumulativeActiveBettors {
  period: number
  start_date: string
  end_date: string
  new_bettors: number
  cumulative_active_bettors: number
  active_addresses: number
}

export interface TimeframeAnalytics {
  activity_over_time: PeriodData[]
}

export interface TimeframeCardCounts {
  period_number: number
  period_start: string
  period_end: string
  card_counts: number[]
}

export interface TimeframeData {
  activity_over_time: PeriodData[]
  slips_by_card_count: TimeframeCardCounts[]
}

export interface AnalyticsData {
  timeframe: string
  start_date: string
  total_periods: number
  total_metrics: {
    total_submissions: number
    total_active_addresses: number
    total_mon_volume: number
    total_jerry_volume: number
    total_cards: number
  }
  average_metrics: {
    avg_submissions_per_day: number
    avg_users_per_day: number
    avg_players_per_day: number
    avg_cards_per_slip: number
    total_days: number
    total_users: number
    total_bet_tx: number
    total_cards: number
  }
  activity_over_time: PeriodData[]
  player_activity: {
    categories: PlayerCategory[]
    total_players: number
  }
  overall_slips_by_card_count: SlipCardCount[]
  top_bettors: TopBettor[]
  rbs_stats_by_periods?: RbsStatsPeriod[]
  cohort_retention?: CohortRetentionData[]
  cumulative_active_bettors?: CumulativeActiveBettors[]
  
  // Multi-timeframe data
  daily_analytics?: TimeframeAnalytics
  weekly_analytics?: TimeframeAnalytics
  monthly_analytics?: TimeframeAnalytics
  
  // New timeframe-specific card count data
  daily_slips_by_card_count?: TimeframeCardCounts[]
  weekly_slips_by_card_count_new?: TimeframeCardCounts[]
  monthly_slips_by_card_count?: TimeframeCardCounts[]
  
  timeframes?: {
    [key: string]: TimeframeData
  }
  
  // Claiming data
  claiming_data?: ClaimingData[]
}

export interface DailyData {
  start_date: string
  submissions: number
  mon_volume: number
  jerry_volume: number
  [key: string]: any
}

export interface ClaimingData {
  date: string
  mon_volume: number
  jerry_volume: number
  transactions: number
  unique_users: number
  active_claimers: number
  new_claimers: number
}

export interface CalendarCell {
  date: string
  value: number
}
