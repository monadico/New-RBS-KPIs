export interface WeeklyData {
  week_start: string;
  week_end: string;
  week_number: number;
  transaction_count: number;
  active_bettors: number;
  new_users?: number;
  mon_volume: number;
  jerry_volume: number;
  total_cards: number;
  avg_bet_amount: number;
  mon_transactions: number;
  jerry_transactions: number;
  avg_cards_per_tx?: number;
}

export interface DailyData {
  date: string;
  transaction_count: number;
  active_bettors: number;
  mon_volume: number;
  jerry_volume: number;
  total_cards: number;
  avg_bet_amount: number;
  mon_transactions: number;
  jerry_transactions: number;
}

export interface HeatmapData {
  week_start: string;
  days: { [key: number]: number };
}

export interface PeriodStats {
  period: string;
  mon_volume: number;
  jerry_volume: number;
  transaction_count: number;
  active_bettors: number;
  total_cards: number;
}

export interface TotalsStats {
  total_unique_users: number;
  total_transactions: number;
  total_cards: number;
  total_mon_volume: number;
  total_jerry_volume: number;
  total_mon_transactions: number;
  total_jerry_transactions: number;
}

export interface TokenVolumeWeek {
  week_start: string;
  mon_volumes: { [key: string]: number };
  jerry_volumes: { [key: string]: number };
}

export interface RetentionWeek {
  earliest_date: string;
  new_users: number;
  one_week_later?: number;
  two_week_later?: number;
  three_week_later?: number;
  four_week_later?: number;
  five_week_later?: number;
  six_week_later?: number;
  seven_week_later?: number;
  eight_week_later?: number;
  nine_week_later?: number;
  ten_week_later?: number;
  over_ten_week_later?: number;
}

export interface RetentionAverages {
  one_week_retention: number;
  two_week_retention: number;
  three_week_retention: number;
  four_week_retention: number;
}

export interface RetentionData {
  weeks: RetentionWeek[];
  averages: RetentionAverages;
}

export interface DashboardStats {
  total_transactions: number;
  total_volume: number;
  unique_users: number;
  average_bet: number;
  total_cards: number;
  token_stats: TokenStats[];
}

export interface TokenStats {
  token: string;
  count: number;
  total_volume: number;
  average_bet: number;
  percentage: number;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
    tension?: number;
    type?: string;
    yAxisID?: string;
  }[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
} 