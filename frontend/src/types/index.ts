export interface WeeklyData {
  week_start: string;
  week_end: string;
  week_number: number;
  transaction_count: number;
  unique_users: number;
  total_volume: number;
  avg_bet_amount: number;
  mon_transactions: number;
  jerry_transactions: number;
  mon_volume: number;
  jerry_volume: number;
  total_cards: number;
  avg_cards: number;
}

export interface DailyData {
  date: string;
  transaction_count: number;
  unique_users: number;
  total_volume: number;
  total_cards: number;
  avg_bet_amount: number;
  mon_volume: number;
  jerry_volume: number;
}

export interface HeatmapData {
  day_of_week: number;
  day_name: string;
  transaction_count: number;
  unique_users: number;
  total_volume: number;
  total_cards: number;
}

export interface PeriodStats {
  period: string;
  transactions: number;
  users: number;
  volume: number;
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