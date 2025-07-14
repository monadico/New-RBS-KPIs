import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, BarElement } from 'chart.js';
// import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Pie, Chart } from 'react-chartjs-2';
import './App.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, BarElement);
// ChartJS.register(ChartDataLabels); // Remove datalabels plugin registration

// Fix for Chrome extension ethereum property conflict
if (typeof window !== 'undefined') {
  // Prevent Chrome extension from redefining ethereum property
  const originalDefineProperty = Object.defineProperty;
  Object.defineProperty = function(obj: any, prop: PropertyKey, descriptor: PropertyDescriptor): any {
    if (obj === window && prop === 'ethereum' && (window as any).ethereum) {
      return window; // Skip redefinition if ethereum already exists
    }
    return originalDefineProperty.call(this, obj, prop, descriptor);
  };
  
  // Global error handler to prevent unhandled errors
  window.addEventListener('error', (event) => {
    console.error('Global error caught:', event.error);
    event.preventDefault();
  });
  
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
  });
}

interface AnalyticsData {
  timeframe: string;
  start_date: string;
  total_periods: number;
  total_metrics: {
    total_submissions: number;
    total_active_addresses: number;
    total_mon_volume: number;
    total_jerry_volume: number;
    total_cards: number;
  };
  player_activity: {
    categories: Array<{
      category: string;
      player_count: number;
      percentage: number;
    }>;
    total_players: number;
  };
  average_metrics: {
    avg_submissions_per_day: number;
    avg_users_per_day: number;
    avg_players_per_day: number;
    avg_cards_per_slip: number;
    total_days: number;
    total_users: number;
    total_bet_tx: number;
    total_cards: number;
  };
  activity_over_time: Array<{
    period: number;
    start_date: string;
    end_date: string;
    submissions: number;
    active_addresses: number;
    new_bettors: number;
    mon_volume: number;
    jerry_volume: number;
    total_volume: number;
    total_cards: number;
    avg_cards_per_submission: number;
    avg_bet_amount: number;
    mon_transactions: number;
    jerry_transactions: number;
  }>;
  overall_slips_by_card_count: Array<{
    cards_in_slip: number;
    bets: number;
    percentage: number;
  }>;
  // Legacy weekly format (for backward compatibility)
  weekly_slips_by_card_count?: Array<{
    week_number: number;
    week_start: string;
    week_end: string;
    card_counts: number[];
  }>;
  top_bettors: Array<{
    user_address: string;
    rank: number;
    total_mon: number;
    total_jerry: number;
    total_bets: number;
    avg_cards_per_slip: number;
    active_days: number;
  }>;
  // New fields from enhanced analytics
  rbs_stats_by_periods?: Array<{
    period: string;
    mon_volume: number;
    jerry_volume: number;
    total_volume: number;
    submissions: number;
    active_bettors: number;
    total_cards: number;
  }>;
  cumulative_active_bettors?: Array<{
    period: number;
    start_date: string;
    end_date: string;
    new_bettors: number;
    cumulative_active_bettors: number;
    active_addresses: number;
  }>;
  // Multi-timeframe data
  daily_analytics?: {
    activity_over_time: Array<{
      period: number;
      start_date: string;
      end_date: string;
      submissions: number;
      active_addresses: number;
      new_bettors: number;
      mon_volume: number;
      jerry_volume: number;
      total_volume: number;
      total_cards: number;
      avg_cards_per_submission: number;
    }>;
  };
  weekly_analytics?: {
    activity_over_time: Array<{
      period: number;
      start_date: string;
      end_date: string;
      submissions: number;
      active_addresses: number;
      new_bettors: number;
      mon_volume: number;
      jerry_volume: number;
      total_volume: number;
      total_cards: number;
      avg_cards_per_submission: number;
    }>;
  };
  monthly_analytics?: {
    activity_over_time: Array<{
      period: number;
      start_date: string;
      end_date: string;
      submissions: number;
      active_addresses: number;
      new_bettors: number;
      mon_volume: number;
      jerry_volume: number;
      total_volume: number;
      total_cards: number;
      avg_cards_per_submission: number;
    }>;
  };
  // New timeframe-specific card count data
  daily_slips_by_card_count?: Array<{
    period_number: number;
    period_start: string;
    period_end: string;
    card_counts: number[];
  }>;
  weekly_slips_by_card_count_new?: Array<{
    period_number: number;
    period_start: string;
    period_end: string;
    card_counts: number[];
  }>;
  monthly_slips_by_card_count?: Array<{
    period_number: number;
    period_start: string;
    period_end: string;
    card_counts: number[];
  }>;
  timeframes?: {
    [key: string]: {
      activity_over_time: Array<{
        period: number;
        start_date: string;
        end_date: string;
        submissions: number;
        active_addresses: number;
        new_bettors: number;
        mon_volume: number;
        jerry_volume: number;
        total_volume: number;
        total_cards: number;
        avg_cards_per_submission: number;
      }>;
      slips_by_card_count: Array<{
        period_number: number;
        period_start: string;
        period_end: string;
        card_counts: number[];
      }>;
    };
  };
}

interface DailyData {
  start_date: string;
  submissions: number;
  mon_volume: number;
  jerry_volume: number;
  [key: string]: any;
}
interface CalendarCell {
  date: string;
  value: number;
}

function App() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'daily' | 'weekly' | 'monthly'>('weekly');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await fetch('/analytics_dump.json');
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        const json = await res.json();
        if (!json.success) throw new Error(json.error || 'JSON error');
        setData(json);
        setError(null);
      } catch (err: any) {
        console.error('Error loading analytics data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load analytics data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Loading analytics data...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!data) {
    return <div className="error">No data available</div>;
  }

  // Get the appropriate data based on selected timeframe
  const getTimeframeData = () => {
    // Try new optimized structure first
    if (data.timeframes && data.timeframes[selectedTimeframe]) {
      return data.timeframes[selectedTimeframe].activity_over_time || data.activity_over_time;
    }
    
    // Fallback to legacy structure
    switch (selectedTimeframe) {
      case 'daily':
        return data.daily_analytics?.activity_over_time || data.activity_over_time;
      case 'monthly':
        return data.monthly_analytics?.activity_over_time || data.activity_over_time;
      case 'weekly':
      default:
        return data.weekly_analytics?.activity_over_time || data.activity_over_time;
    }
  };

  const timeframeData = getTimeframeData();

  // --- LINE 3 CHART DATA ---
  // 1. Player activity pie chart (already in data)
  const playerActivityPieData = {
    labels: data.player_activity.categories.map(cat => cat.category),
    datasets: [
      {
        data: data.player_activity.categories.map(cat => cat.player_count),
        backgroundColor: [
          '#6366f1', // Primary
          '#10b981', // Secondary
          '#f59e0b', // Accent
          '#8b5cf6'  // Purple
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };

  // 3. Pie: Overall distribution of slips by card count (mock data)
  const overallSlipsByCardCount = data.overall_slips_by_card_count || [];
  const overallSlipsPieData = {
    labels: overallSlipsByCardCount.map(item => String(item.cards_in_slip)),
    datasets: [
      {
        data: overallSlipsByCardCount.map(item => item.bets),
        backgroundColor: [
          '#6366f1', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'
        ],
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };
  const overallPieOptions = {
    plugins: {
      legend: { position: 'top' as const },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const idx = context.dataIndex;
            const label = overallSlipsByCardCount[idx]?.cards_in_slip;
            const bets = overallSlipsByCardCount[idx]?.bets;
            const percent = overallSlipsByCardCount[idx]?.percentage;
            return `Cards: ${label} | Bets: ${bets.toLocaleString()} | ${percent}%`;
          }
        }
      }
    }
  };

  // 2. Stacked bar: Distribution of slips by card count per period (dynamic based on timeframe)
  const cardCounts = [2, 3, 4, 5, 6, 7];
  
  // Get the appropriate card count data based on selected timeframe
  const getCardCountData = () => {
    // Try new optimized structure first
    if (data.timeframes && data.timeframes[selectedTimeframe]) {
      return data.timeframes[selectedTimeframe].slips_by_card_count || [];
    }
    
    // Fallback to legacy structure
    switch (selectedTimeframe) {
      case 'daily':
        return data.daily_slips_by_card_count || [];
      case 'monthly':
        return data.monthly_slips_by_card_count || [];
      case 'weekly':
      default:
        // Handle both new and legacy formats
        const newWeeklyData = data.weekly_slips_by_card_count_new || [];
        const legacyWeeklyData = data.weekly_slips_by_card_count || [];
        return newWeeklyData.length > 0 ? newWeeklyData : legacyWeeklyData;
    }
  };
  
  const timeframeCardCountData = getCardCountData();
  
  // If no timeframe-specific data is available, fall back to weekly data for all timeframes
  const finalCardCountData = timeframeCardCountData.length > 0 ? timeframeCardCountData : (data.weekly_slips_by_card_count || []);
  
  // For slips by card count chart
  const periods = finalCardCountData.map(period => {
    // Use period_start if available, else fallback to week_start (legacy weekly format)
    if ('period_start' in period) return period.period_start;
    if ('week_start' in period) return period.week_start;
    return '';
  });
  
  const slipsByCardCount = cardCounts.map((count, idx) => {
    const dataArr = finalCardCountData.map(period => period.card_counts[idx] || 0);
    return {
      label: `${count} cards`,
      data: dataArr,
      backgroundColor: [
        '#6366f1', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'
      ][idx],
      stack: 'slips',
      borderWidth: 1
    };
  });
  const slipsByCardCountBarData = {
    labels: periods,
    datasets: slipsByCardCount
  };

  // --- Submission Activity Over Time (Bar+Line) ---
  const submissionActivityData = {
    labels: timeframeData.map(period => period.start_date),
    datasets: [
      {
        label: 'Submissions',
        data: timeframeData.map(period => period.submissions),
        backgroundColor: 'rgba(99, 102, 241, 0.6)',
        borderColor: 'rgba(99, 102, 241, 1)',
        borderWidth: 2,
        type: 'bar' as const,
        yAxisID: 'y',
      },
      {
        label: 'Active Bettors',
        data: timeframeData.map(period => period.active_addresses),
        borderColor: 'rgba(16, 185, 129, 1)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 3,
        type: 'line' as const,
        yAxisID: 'y1',
        tension: 0.4,
        fill: false,
        pointRadius: 3,
      }
    ]
  };

  // --- New Bettors Over Time (Bar+Line) ---
  let cumulativeBettors = 0;
  const cumulativeData = timeframeData.map(period => {
    cumulativeBettors += period.new_bettors;
    return cumulativeBettors;
  });
  const newBettorsData = {
    labels: timeframeData.map(period => period.start_date),
    datasets: [
      {
        label: 'New Bettors',
        data: timeframeData.map(period => period.new_bettors),
        backgroundColor: 'rgba(16, 185, 129, 0.6)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 2,
        type: 'bar' as const,
        yAxisID: 'y',
      },
      {
        label: 'Cumulative Bettors',
        data: cumulativeData,
        borderColor: 'rgba(245, 158, 11, 1)',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        borderWidth: 3,
        type: 'line' as const,
        yAxisID: 'y1',
        tension: 0.4,
        fill: false,
        pointRadius: 3,
      }
    ]
  };

  // --- Pie chart options with outlabels ---
  const pieOptions = {
    plugins: {
      legend: { position: 'top' as const },
      // datalabels removed
    },
  };

  // --- Bar+Line chart options ---
  const barLineOptions = (yLabel: string, y1Label: string) => ({
    responsive: true,
    interaction: { mode: 'index' as const, intersect: false },
    plugins: {
      legend: { position: 'top' as const },
      title: { display: false },
    },
    scales: {
      x: { stacked: false },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: { display: true, text: yLabel },
        beginAtZero: true,
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: { display: true, text: y1Label },
        grid: { drawOnChartArea: false },
        beginAtZero: true,
      },
    },
  });

  // --- Stacked bar chart options for slips by card count ---
  const stackedBarOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: { display: false },
      // datalabels removed
    },
    interaction: { mode: 'index' as const, intersect: false },
    scales: {
      x: { stacked: true },
      y: { stacked: true, beginAtZero: true, title: { display: true, text: 'Slips' } },
    },
  };

  // --- MON & JERRY Volume Over Time (Stacked Area) ---
  const monJerryVolumeData = {
    labels: timeframeData.map(period => period.start_date),
    datasets: [
      {
        label: '$MON Volume',
        data: timeframeData.map(period => period.mon_volume),
        borderColor: 'rgba(99, 102, 241, 1)',
        backgroundColor: 'rgba(99, 102, 241, 0.25)',
        borderWidth: 2,
        fill: 'origin', // ensure area is rendered
        tension: 0.4,
        pointRadius: 0,
      },
      {
        label: '$JERRY Volume',
        data: timeframeData.map(period => period.jerry_volume),
        borderColor: 'rgba(16, 185, 129, 1)',
        backgroundColor: 'rgba(16, 185, 129, 0.25)',
        borderWidth: 2,
        fill: 'origin', // ensure area is rendered
        tension: 0.4,
        pointRadius: 0,
      }
    ]
  };

  // --- NEW: Active Bettors Over Time (Line Chart) ---
  // Calculate cumulative active bettors from the selected timeframe data
  let cumulativeActiveBettors = 0;
  const activeBettorsCumulativeData = timeframeData.map(period => {
    cumulativeActiveBettors += period.new_bettors;
    return cumulativeActiveBettors;
  });
  
  const activeBettorsChartData = {
    labels: timeframeData.map(period => period.start_date),
    datasets: [
      {
        label: 'Cumulative Active Bettors',
        data: activeBettorsCumulativeData,
        borderColor: 'rgba(139, 92, 246, 1)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        fill: false,
        pointRadius: 4,
      }
    ]
  };

  // --- NEW: Total and Average Cards Over Time (Bar + Line) ---
  const cardsOverTimeData = {
    labels: timeframeData.map(period => period.start_date),
    datasets: [
      {
        label: 'Total Cards',
        data: timeframeData.map(period => period.total_cards),
        backgroundColor: 'rgba(245, 158, 11, 0.6)',
        borderColor: 'rgba(245, 158, 11, 1)',
        borderWidth: 2,
        type: 'bar' as const,
        yAxisID: 'y',
      },
      {
        label: 'Average Cards per Submission',
        data: timeframeData.map(period => period.avg_cards_per_submission),
        borderColor: 'rgba(139, 92, 246, 1)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderWidth: 3,
        type: 'line' as const,
        yAxisID: 'y1',
        tension: 0.4,
        fill: false,
        pointRadius: 3,
      }
    ]
  };

  // --- Stacked Area Chart options for MON & JERRY Volume ---
  const stackedAreaOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' as const },
      title: { display: false },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label;
            const value = context.parsed.y;
            return `${label}: $${value.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: { 
        stacked: false,
        title: { display: true, text: 'Week' }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: { display: true, text: 'Volume ($)' },
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return `$${value.toLocaleString()}`;
          }
        }
      }
    },
    interaction: { mode: 'index' as const, intersect: false },
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toLocaleString();
  };

  const formatCurrency = (num: number): string => {
    return `$${num.toLocaleString()}`;
  };

  // Helper to format addresses
  const formatAddress = (addr: string) => addr.slice(0, 6) + '...' + addr.slice(-4);

  // Top 20 Bettors Table
  const topBettors = data.top_bettors || [];

  // --- HEATMAP AGGREGATION LOGIC ---
  const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const submissionByDay = Array(7).fill(0);
  const monVolumeByDay = Array(7).fill(0);
  const jerryVolumeByDay = Array(7).fill(0);

  // Use daily analytics if available, else fallback to activity_over_time
  const dailyData: DailyData[] = data.timeframes?.daily?.activity_over_time || data.daily_analytics?.activity_over_time || data.activity_over_time || [];
  dailyData.forEach((day: DailyData) => {
    const date = new Date(day.start_date);
    // getDay(): 0=Sunday, 1=Monday, ..., 6=Saturday
    // We want Monday=0, ..., Sunday=6
    let dow = date.getDay();
    dow = (dow + 6) % 7; // shift so Monday=0
    submissionByDay[dow] += day.submissions;
    monVolumeByDay[dow] += day.mon_volume;
    jerryVolumeByDay[dow] += day.jerry_volume;
  });

  // --- TYPES ---
  // --- CALENDAR HEATMAP LOGIC ---
  function buildCalendarMatrix(
    dailyData: DailyData[],
    valueKey: keyof DailyData
  ): CalendarCell[][] {
    // Map date string to value
    const dateToValue: Record<string, number> = {};
    let minDate: Date | null = null, maxDate: Date | null = null;
    dailyData.forEach((day: DailyData) => {
      dateToValue[day.start_date] = day[valueKey] as number;
      const d = new Date(day.start_date);
      if (!minDate || d < minDate) minDate = d;
      if (!maxDate || d > maxDate) maxDate = d;
    });
    if (!minDate || !maxDate) return [];
    // Find the Monday before or on minDate
    let first = new Date(minDate);
    let day = first.getDay();
    // getDay(): 0=Sunday, 1=Monday, ..., 6=Saturday
    // If not Monday, go back to previous Monday
    if (day !== 1) {
      // If Sunday (0), go back 6 days; else go back (day-1) days
      const diff = day === 0 ? 6 : day - 1;
      first.setDate(first.getDate() - diff);
    }
    // Find the last Sunday after or on maxDate
    let last = new Date(maxDate);
    day = last.getDay();
    let offsetLast = day === 0 ? 0 : 7 - day;
    last.setDate(last.getDate() + offsetLast);
    // Build matrix: rows=days (Mon-Sun), cols=weeks
    const weeks: CalendarCell[][] = [];
    let d = new Date(first);
    while (d <= last) {
      const week: CalendarCell[] = [];
      for (let i = 0; i < 7; i++) {
        const dateStr = d.toISOString().slice(0, 10);
        week.push({
          date: dateStr,
          value: dateToValue[dateStr] || 0
        });
        d.setDate(d.getDate() + 1);
      }
      weeks.push(week);
    }
    // Transpose: [7][N] (days, weeks)
    const matrix: CalendarCell[][] = Array(7).fill(0).map((_, i) => weeks.map((w: CalendarCell[]) => w[i]));
    return matrix;
  }

  function CalendarHeatmap({
    matrix,
    title,
    colorScale,
    valueFormatter
  }: {
    matrix: CalendarCell[][];
    title: string;
    colorScale: (v: number) => string;
    valueFormatter?: (v: number) => string;
  }) {
    // Find max value for color scaling
    const max = Math.max(...matrix.flat().map((cell: CalendarCell) => cell.value));

    // Tooltip state
    const [tooltip, setTooltip] = React.useState<{
      x: number;
      y: number;
      date: string;
      value: number;
    } | null>(null);

    // Tooltip element
    const tooltipEl = tooltip ? (
      <div
        style={{
          position: 'fixed',
          left: tooltip.x + 12,
          top: tooltip.y + 12,
          background: 'rgba(30,41,59,0.95)',
          color: '#fff',
          padding: '8px 12px',
          borderRadius: 8,
          fontSize: 14,
          pointerEvents: 'none',
          zIndex: 1000,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
        }}
      >
        <div style={{ fontWeight: 600 }}>{tooltip.date}</div>
        <div>{valueFormatter ? valueFormatter(tooltip.value) : tooltip.value}</div>
      </div>
    ) : null;

    return (
      <div className="card" style={{ marginBottom: 24, position: 'relative' }}>
        <h2 style={{ marginBottom: 16 }}>{title}</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {matrix.map((row, dayIdx) => (
            <div key={dayIdx} style={{ display: 'flex', flexDirection: 'row', gap: 2 }}>
              {row.map((cell, weekIdx) => (
                <div
                  key={weekIdx}
                  onMouseEnter={e => {
                    setTooltip({
                      x: e.clientX,
                      y: e.clientY,
                      date: cell.date,
                      value: cell.value
                    });
                  }}
                  onMouseMove={e => {
                    setTooltip(t => t ? { ...t, x: e.clientX, y: e.clientY } : null);
                  }}
                  onMouseLeave={() => setTooltip(null)}
                  style={{
                    width: 22, height: 22, borderRadius: 4,
                    background: colorScale(cell.value / (max || 1)),
                    cursor: cell.value > 0 ? 'pointer' : 'default',
                    border: '1px solid #e5e7eb',
                    transition: 'background 0.2s',
                  }}
                />
              ))}
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginTop: 8, color: '#64748b' }}>
          {daysOfWeek.map((d: string) => <span key={d}>{d.slice(0,3)}</span>)}
        </div>
        {tooltipEl}
      </div>
    );
  }

  // Build matrices for each heatmap
  const submissionMatrix = buildCalendarMatrix(dailyData, 'submissions');
  const monMatrix = buildCalendarMatrix(dailyData, 'mon_volume');
  const jerryMatrix = buildCalendarMatrix(dailyData, 'jerry_volume');

  // After building the matrices, add these debug logs:
  console.log('First week (all days):', submissionMatrix.map(row => row[0]));
  console.log('First column (all weeks):', submissionMatrix[0].map(cell => cell.date));

  // --- HEATMAP COMPONENT ---
  function SimpleHeatmap({ values, title, colorScale, valueFormatter }: { values: number[], title: string, colorScale: (v: number) => string, valueFormatter?: (v: number) => string }) {
    const max = Math.max(...values);
    return (
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ marginBottom: 16 }}>{title}</h2>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
          {values.map((v, i) => (
            <div key={i} style={{
              flex: 1,
              background: colorScale(v / (max || 1)),
              color: v / (max || 1) > 0.5 ? '#111' : '#fff',
              borderRadius: 8,
              padding: 12,
              textAlign: 'center',
              fontWeight: 600,
              fontSize: 16,
              boxShadow: '0 1px 4px rgba(0,0,0,0.06)'
            }}>
              <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 6 }}>{daysOfWeek[i]}</div>
              <div style={{ fontSize: 18 }}>{valueFormatter ? valueFormatter(v) : v}</div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  // --- COLOR SCALE ---
  function blueToYellow(t: number) {
    // t: 0 (min) to 1 (max)
    // interpolate from #6366f1 (blue) to #f59e0b (yellow)
    const c1 = [99, 102, 241]; // blue
    const c2 = [245, 158, 11]; // yellow
    const rgb = c1.map((c, i) => Math.round(c + (c2[i] - c) * t));
    return `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`;
  }

  return (
    <div className="container">
      {/* Dashboard Header */}
      <div className="dashboard-header">
        <h1>📊 RBS Analytics Dashboard</h1>
        <div className="dashboard-subtitle">
          Real-time insights into RareBetSports ecosystem performance
        </div>
      </div>
      
      {/* Timeframe Selector */}
      <div className="timeframe-selector">
        {(['daily', 'weekly', 'monthly'] as const).map((timeframe) => (
          <button
            key={timeframe}
            onClick={() => setSelectedTimeframe(timeframe)}
            className={`timeframe-button ${selectedTimeframe === timeframe ? 'active' : ''}`}
          >
            {timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}
          </button>
        ))}
      </div>
      
      {/* Line 1: Four Big Metric Cards */}
      <div className="metrics-row">
        <div className="big-metric-card">
          <div className="big-metric-value">{formatNumber(data.total_metrics.total_submissions)}</div>
          <div className="big-metric-title">Total RareLink Submissions</div>
        </div>
        <div className="big-metric-card">
          <div className="big-metric-value">{formatNumber(data.total_metrics.total_active_addresses)}</div>
          <div className="big-metric-title">Total Active Addresses</div>
        </div>
        <div className="big-metric-card">
          <div className="big-metric-value">{formatCurrency(data.total_metrics.total_mon_volume)}</div>
          <div className="big-metric-title">Total $MON Volume</div>
        </div>
        <div className="big-metric-card">
          <div className="big-metric-value">{formatCurrency(data.total_metrics.total_jerry_volume)}</div>
          <div className="big-metric-title">Total $JERRY Volume</div>
        </div>
      </div>

      {/* Line 1.5: Three Additional Average Metrics */}
      <div className="metrics-row">
        <div className="big-metric-card">
          <div className="big-metric-value">{formatNumber(data.average_metrics.avg_submissions_per_day)}</div>
          <div className="big-metric-title">Avg Submissions per Day</div>
        </div>
        <div className="big-metric-card">
          <div className="big-metric-value">{formatNumber(data.average_metrics.avg_players_per_day)}</div>
          <div className="big-metric-title">Avg Players per Day</div>
        </div>
        <div className="big-metric-card">
          <div className="big-metric-value">{data.average_metrics.avg_cards_per_slip.toFixed(1)}</div>
          <div className="big-metric-title">Avg Cards per RareLink Slip</div>
        </div>
      </div>

      {/* Line 2: Two Charts */}
      <div className="charts-row">
        <div className="chart-container">
          <h2 className="chart-title">📈 RareLink Submission Activity Over Time</h2>
          <Chart
            type="bar"
            data={submissionActivityData}
            options={barLineOptions('Submissions', 'Active Bettors')}
          />
        </div>

        <div className="chart-container">
          <h2 className="chart-title">👥 New Bettors Over Time</h2>
          <Chart
            type="bar"
            data={newBettorsData}
            options={barLineOptions('New Bettors', 'Cumulative Bettors')}
          />
        </div>
      </div>

      {/* LINE 3: Three Charts */}
      <div className="three-charts-row">
        {/* 1. Player Activity Pie */}
        <div className="chart-container">
          <h2 className="chart-title">👥 Players activity based on RareLinks submission</h2>
          <Pie data={playerActivityPieData} options={pieOptions} />
        </div>
        {/* 2. Stacked Bar: Slips by Card Count per Week - make this span 2 columns for more space */}
        <div className="chart-container" style={{ gridColumn: 'span 2' }}>
          <h2 className="chart-title">Distribution of RareLink slips by card count</h2>
          <Chart
            type="bar"
            data={slipsByCardCountBarData}
            options={stackedBarOptions}
          />
        </div>
        {/* 3. Pie: Overall Slips by Card Count */}
        <div className="chart-container">
          <h2 className="chart-title">Overall distribution of RareLink Slips by # of cards</h2>
          <Pie data={overallSlipsPieData} options={overallPieOptions} />
        </div>
      </div>

      {/* NEW: Stacked Area Chart for MON & JERRY Volume Over Time */}
      <div className="chart-container">
        <h2 className="chart-title">💰 $MON & $JERRY Volume Deposited in RareLinks Over Time</h2>
        <Chart
          type="line"
          data={monJerryVolumeData}
          options={stackedAreaOptions}
        />
      </div>

      {/* NEW: Active Bettors Over Time (Line Chart) */}
      <div className="chart-container">
        <h2 className="chart-title">👥 Active Bettors Over Time</h2>
        <Chart
          type="line"
          data={activeBettorsChartData}
          options={barLineOptions('Cumulative Active Bettors', '')}
        />
      </div>

      {/* NEW: Total and Average Cards Over Time (Bar + Line) */}
      <div className="chart-container">
        <h2 className="chart-title">📄 Total and Average Cards Over Time</h2>
        <Chart
          type="bar"
          data={cardsOverTimeData}
          options={barLineOptions('Total Cards', 'Average Cards per Submission')}
        />
      </div>

      {/* NEW: RBS Stats by Different Periods Table */}
      {data.rbs_stats_by_periods && data.rbs_stats_by_periods.length > 0 && (
        <div className="card" style={{ marginTop: 30 }}>
          <h2>📊 RBS Stats by Different Periods</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', fontSize: '0.95rem', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f3f4f6' }}>
                  <th style={{ padding: '8px' }}>Period</th>
                  <th style={{ padding: '8px' }}>MON Volume</th>
                  <th style={{ padding: '8px' }}>JERRY Volume</th>
                  <th style={{ padding: '8px' }}>Total Volume</th>
                  <th style={{ padding: '8px' }}>Submissions</th>
                  <th style={{ padding: '8px' }}>Active Bettors</th>
                  <th style={{ padding: '8px' }}>Total Cards</th>
                </tr>
              </thead>
              <tbody>
                {data.rbs_stats_by_periods.map((period: any, index: number) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '8px', fontWeight: 'bold' }}>{period.period}</td>
                    <td style={{ padding: '8px', textAlign: 'right' }}>{formatCurrency(period.mon_volume)}</td>
                    <td style={{ padding: '8px', textAlign: 'right' }}>{formatCurrency(period.jerry_volume)}</td>
                    <td style={{ padding: '8px', textAlign: 'right' }}>{formatCurrency(period.total_volume)}</td>
                    <td style={{ padding: '8px', textAlign: 'right' }}>{formatNumber(period.submissions)}</td>
                    <td style={{ padding: '8px', textAlign: 'right' }}>{formatNumber(period.active_bettors)}</td>
                    <td style={{ padding: '8px', textAlign: 'right' }}>{formatNumber(period.total_cards)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top 20 Bettors Table */}
      <div className="card" style={{ marginTop: 30 }}>
        <h2>🏆 Top 20 Bettors</h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', fontSize: '0.95rem', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f3f4f6' }}>
                <th style={{ padding: '8px' }}>Rank</th>
                <th style={{ padding: '8px' }}>Address</th>
                <th style={{ padding: '8px' }}>Total MON</th>
                <th style={{ padding: '8px' }}>Total JERRY</th>
                <th style={{ padding: '8px' }}>Total Bets</th>
                <th style={{ padding: '8px' }}>Avg Cards/Slip</th>
                <th style={{ padding: '8px' }}>Active Days</th>
              </tr>
            </thead>
            <tbody>
              {topBettors.map((b: any) => (
                <tr key={b.user_address} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px', textAlign: 'center' }}>{b.rank}</td>
                  <td style={{ padding: '8px', fontFamily: 'monospace', wordBreak: 'break-all' }} title={b.user_address}>{b.user_address}</td>
                  <td style={{ padding: '8px', textAlign: 'right' }}>{b.total_mon.toLocaleString()}</td>
                  <td style={{ padding: '8px', textAlign: 'right' }}>{b.total_jerry.toLocaleString()}</td>
                  <td style={{ padding: '8px', textAlign: 'right' }}>{b.total_bets.toLocaleString()}</td>
                  <td style={{ padding: '8px', textAlign: 'right' }}>{b.avg_cards_per_slip.toFixed(2)}</td>
                  <td style={{ padding: '8px', textAlign: 'right' }}>{b.active_days}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Place heatmaps after the last chart, before Top 20 Bettors table */}
      <div className="card" style={{ marginTop: 30 }}>
        <SimpleHeatmap
          values={submissionByDay}
          title="🗓️ Bet Submission Transactions by Day of Week"
          colorScale={blueToYellow}
          valueFormatter={formatNumber}
        />
        <SimpleHeatmap
          values={monVolumeByDay}
          title="$MON Volume by Day of Week"
          colorScale={blueToYellow}
          valueFormatter={formatCurrency}
        />
        <SimpleHeatmap
          values={jerryVolumeByDay}
          title="$JERRY Volume by Day of Week"
          colorScale={blueToYellow}
          valueFormatter={formatCurrency}
        />
      </div>
      {/* Place calendar heatmaps after the last chart, before Top 20 Bettors table */}
      <div className="card" style={{ marginTop: 30 }}>
        <CalendarHeatmap
          matrix={submissionMatrix}
          title="🗓️ Bet Submission Transactions Calendar Heatmap"
          colorScale={blueToYellow}
          valueFormatter={formatNumber}
        />
        <CalendarHeatmap
          matrix={monMatrix}
          title="$MON Volume Calendar Heatmap"
          colorScale={blueToYellow}
          valueFormatter={formatCurrency}
        />
        <CalendarHeatmap
          matrix={jerryMatrix}
          title="$JERRY Volume Calendar Heatmap"
          colorScale={blueToYellow}
          valueFormatter={formatCurrency}
        />
      </div>
    </div>
  );
}

export default App; 