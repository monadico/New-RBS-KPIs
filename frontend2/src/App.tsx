import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, BarElement } from 'chart.js';
// import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Pie, Chart } from 'react-chartjs-2';
import './App.css';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Title, BarElement);
// ChartJS.register(ChartDataLabels); // Remove datalabels plugin registration

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
        const json = await res.json();
        if (!json.success) throw new Error(json.error || 'JSON error');
        setData(json);
        setError(null);
      } catch (err: any) {
        setError('Failed to load analytics data');
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
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0'
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
          '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
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
  
  const periods = finalCardCountData.map(period => {
    // Handle both new format (period_number) and legacy format (week_number)
    const periodNum = 'period_number' in period ? period.period_number : period.week_number;
    return `${selectedTimeframe.charAt(0).toUpperCase() + selectedTimeframe.slice(1)} ${periodNum}`;
  });
  
  const slipsByCardCount = cardCounts.map((count, idx) => {
    const dataArr = finalCardCountData.map(period => period.card_counts[idx] || 0);
    return {
      label: `${count} cards`,
      data: dataArr,
      backgroundColor: [
        '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
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
    labels: timeframeData.map(period => `${selectedTimeframe.charAt(0).toUpperCase() + selectedTimeframe.slice(1)} ${period.period}`),
    datasets: [
      {
        label: 'Submissions',
        data: timeframeData.map(period => period.submissions),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        type: 'bar' as const,
        yAxisID: 'y',
      },
      {
        label: 'Active Bettors',
        data: timeframeData.map(period => period.active_addresses),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
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
    labels: timeframeData.map(period => `${selectedTimeframe.charAt(0).toUpperCase() + selectedTimeframe.slice(1)} ${period.period}`),
    datasets: [
      {
        label: 'New Bettors',
        data: timeframeData.map(period => period.new_bettors),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
        type: 'bar' as const,
        yAxisID: 'y',
      },
      {
        label: 'Cumulative Bettors',
        data: cumulativeData,
        borderColor: 'rgba(255, 159, 64, 1)',
        backgroundColor: 'rgba(255, 159, 64, 0.1)',
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
    labels: timeframeData.map(period => `${selectedTimeframe.charAt(0).toUpperCase() + selectedTimeframe.slice(1)} ${period.period}`),
    datasets: [
      {
        label: '$MON Volume',
        data: timeframeData.map(period => period.mon_volume),
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.25)',
        borderWidth: 2,
        fill: 'origin', // ensure area is rendered
        tension: 0.4,
        pointRadius: 0,
      },
      {
        label: '$JERRY Volume',
        data: timeframeData.map(period => period.jerry_volume),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.25)',
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
    labels: timeframeData.map(period => `${selectedTimeframe.charAt(0).toUpperCase() + selectedTimeframe.slice(1)} ${period.period}`),
    datasets: [
      {
        label: 'Cumulative Active Bettors',
        data: activeBettorsCumulativeData,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        fill: false,
        pointRadius: 4,
      }
    ]
  };

  // --- NEW: Total and Average Cards Over Time (Bar + Line) ---
  const cardsOverTimeData = {
    labels: timeframeData.map(period => `${selectedTimeframe.charAt(0).toUpperCase() + selectedTimeframe.slice(1)} ${period.period}`),
    datasets: [
      {
        label: 'Total Cards',
        data: timeframeData.map(period => period.total_cards),
        backgroundColor: 'rgba(255, 159, 64, 0.6)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 2,
        type: 'bar' as const,
        yAxisID: 'y',
      },
      {
        label: 'Average Cards per Submission',
        data: timeframeData.map(period => period.avg_cards_per_submission),
        borderColor: 'rgba(153, 102, 255, 1)',
        backgroundColor: 'rgba(153, 102, 255, 0.1)',
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

  return (
    <div className="container">
      <h1>📊 Betting Analytics Dashboard</h1>
      
      {/* Timeframe Selector */}
      <div style={{ marginBottom: 20, textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', background: '#f3f4f6', borderRadius: 8, padding: 4 }}>
          {(['daily', 'weekly', 'monthly'] as const).map((timeframe) => (
            <button
              key={timeframe}
              onClick={() => setSelectedTimeframe(timeframe)}
              style={{
                padding: '8px 16px',
                border: 'none',
                borderRadius: 6,
                background: selectedTimeframe === timeframe ? '#3b82f6' : 'transparent',
                color: selectedTimeframe === timeframe ? 'white' : '#374151',
                cursor: 'pointer',
                fontWeight: selectedTimeframe === timeframe ? 'bold' : 'normal',
                transition: 'all 0.2s'
              }}
            >
              {timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}
            </button>
          ))}
        </div>
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
          <h2>📈 RareLink Submission Activity Over Time</h2>
          <Chart
            type="bar"
            data={submissionActivityData}
            options={barLineOptions('Submissions', 'Active Bettors')}
          />
        </div>

        <div className="chart-container">
          <h2>👥 New Bettors Over Time</h2>
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
        <div className="chart-container" style={{ minHeight: 320, minWidth: 320 }}>
          <h2 className="chart-title">👥 Players activity based on RareLinks submission</h2>
          <Pie data={playerActivityPieData} options={pieOptions} />
        </div>
        {/* 2. Stacked Bar: Slips by Card Count per Week - make this span 2 columns for more space */}
        <div className="chart-container" style={{ gridColumn: 'span 2', minHeight: 400, minWidth: 600 }}>
          <h2 className="chart-title">Distribution of RareLink slips by card count</h2>
          <Chart
            type="bar"
            data={slipsByCardCountBarData}
            options={stackedBarOptions}
          />
        </div>
        {/* 3. Pie: Overall Slips by Card Count */}
        <div className="chart-container" style={{ minHeight: 320, minWidth: 320 }}>
          <h2 className="chart-title">Overall distribution of RareLink Slips by # of cards</h2>
          <Pie data={overallSlipsPieData} options={overallPieOptions} />
        </div>
      </div>

      {/* NEW: Stacked Area Chart for MON & JERRY Volume Over Time */}
      <div className="chart-container" style={{ marginTop: 30, minHeight: 400 }}>
        <h2 className="chart-title">💰 $MON & $JERRY Volume Deposited in RareLinks Over Time</h2>
        <Chart
          type="line"
          data={monJerryVolumeData}
          options={stackedAreaOptions}
        />
      </div>

      {/* NEW: Active Bettors Over Time (Line Chart) */}
      <div className="chart-container" style={{ marginTop: 30, minHeight: 400 }}>
        <h2 className="chart-title">👥 Active Bettors Over Time</h2>
        <Chart
          type="line"
          data={activeBettorsChartData}
          options={barLineOptions('Cumulative Active Bettors', '')}
        />
      </div>

      {/* NEW: Total and Average Cards Over Time (Bar + Line) */}
      <div className="chart-container" style={{ marginTop: 30, minHeight: 400 }}>
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
                  <td style={{ padding: '8px', fontFamily: 'monospace', maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={b.user_address}>{b.user_address}</td>
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
    </div>
  );
}

export default App; 