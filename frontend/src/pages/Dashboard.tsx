import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { DashboardStats, WeeklyData, DailyData, HeatmapData, PeriodStats, TotalsStats, TokenVolumeWeek, RetentionData } from '../types';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Dashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
    return () => {
      const charts = (ChartJS as any).instances;
      if (charts) {
        Object.values(charts).forEach((chart: any) => {
          if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
          }
        });
      }
    };
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/analytics');
      const data = await res.json();
      if (data && data.success !== false) {
        setAnalytics(data);
      } else {
        setError('Failed to fetch analytics');
      }
    } catch (err) {
      setError('Failed to fetch analytics');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number | undefined): string => {
    if (num === undefined || num === null) {
      return '0';
    }
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatCurrency = (num: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  // Updated createHeatmapTable for new HeatmapData structure
  const createHeatmapTable = (data: HeatmapData[], metric: 'transaction_count' | 'unique_users' | 'total_volume') => {
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    // Build a flat array of all values for the metric
    const allValues: number[] = [];
    data.forEach(week => {
      dayNames.forEach((_, i) => {
        allValues.push(week.days[i] || 0);
      });
    });
    const maxValue = Math.max(...allValues);
    return (
      <table className="w-full text-sm">
        <thead>
          <tr className="text-gray-400 border-b border-gray-700">
            <th className="text-left py-2">Week Starting</th>
            {dayNames.map(day => (
              <th key={day} className="text-center py-2">{day}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map(week => (
            <tr key={week.week_start} className="border-b border-gray-700">
              <td className="py-2 text-white">{week.week_start}</td>
              {dayNames.map((_, i) => {
                const value = week.days[i] || 0;
            const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
            const intensity = percentage / 100;
            return (
                  <td key={i} className="py-2 text-center text-white">
                  {metric === 'total_volume' ? formatCurrency(value) : formatNumber(value)}
                    <div className="w-full h-1 bg-gray-700 rounded mt-1"
                      style={{
                        background: `linear-gradient(to right, rgba(79, 70, 229, ${intensity * 0.8 + 0.1}), rgba(79, 70, 229, ${intensity * 0.8 + 0.1}))`
                      }}
                    />
                </td>
            );
          })}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading dashboard data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-red-500 text-xl">{error}</div>
      </div>
    );
  }

  // Helper to safely access analytics fields
  const a = analytics || {};

  // Top Bettors Table
  const renderTopBettors = () => (
    <div className="bg-gray-800 p-4 rounded-lg mb-8">
      <h3 className="font-semibold text-white mb-4">Top Bettors</h3>
      {a.top_bettors && a.top_bettors.length > 0 ? (
        <table className="w-full text-sm text-left text-gray-400">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Address</th>
              <th>Total Volume</th>
              <th>Slips</th>
              <th>Cards</th>
            </tr>
          </thead>
          <tbody>
            {a.top_bettors.map((b: any, i: number) => (
              <tr key={b.address} className="border-b border-gray-700">
                <td>{i + 1}</td>
                <td className="font-mono text-xs">{b.address}</td>
                <td>{formatCurrency(b.total_volume)}</td>
                <td>{formatNumber(b.slip_count)}</td>
                <td>{formatNumber(b.card_count)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : <div className="text-gray-400">No data</div>}
    </div>
  );

  // Chart configurations
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#d1d5db',
          font: { size: 12 }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: '#9ca3af',
          font: { size: 10 },
          callback: (value: any) => value >= 1000 ? `${(value / 1000).toFixed(0)}K` : value
        },
        grid: { color: '#374151' }
      },
      x: {
        ticks: { color: '#9ca3af', font: { size: 10 } },
        grid: { display: false }
      }
    }
  };

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#d1d5db',
          font: { size: 12 },
          padding: 15
        }
      }
    }
  };

  // Add new dashboards below existing ones
  // Totals Dashboard
  const renderTotalsDashboard = () => (
    <div className="bg-gray-800 p-4 rounded-lg mb-8">
      <h3 className="font-semibold text-white mb-4">All-Time Totals</h3>
      {a.totals ? (
        <table className="w-full text-sm text-left text-gray-400">
          <tbody>
            <tr><td>Total Unique Users</td><td>{formatNumber(a.totals.total_unique_users)}</td></tr>
            <tr><td>Total Transactions</td><td>{formatNumber(a.totals.total_transactions)}</td></tr>
            <tr><td>Total Cards</td><td>{formatNumber(a.totals.total_cards)}</td></tr>
            <tr><td>Total MON Volume</td><td>{formatCurrency(a.totals.total_mon_volume)}</td></tr>
            <tr><td>Total JERRY Volume</td><td>{formatCurrency(a.totals.total_jerry_volume)}</td></tr>
            <tr><td>MON Transactions</td><td>{formatNumber(a.totals.total_mon_transactions)}</td></tr>
            <tr><td>JERRY Transactions</td><td>{formatNumber(a.totals.total_jerry_transactions)}</td></tr>
          </tbody>
        </table>
      ) : <div className="text-gray-400">Loading...</div>}
    </div>
  );

  // Token Volume Heatmap Dashboard
  const renderTokenVolumeHeatmap = () => (
    <div className="bg-gray-800 p-4 rounded-lg mb-8">
      <h3 className="font-semibold text-white mb-4">Token Volume Heatmaps (Last 8 Weeks)</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left text-gray-400 mb-4">
          <thead>
            <tr>
              <th>Week Starting</th>
              <th colSpan={7}>MON Volume by Day</th>
            </tr>
            <tr>
              <th></th>
              {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map(day => (
                <th key={day}>{day}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {a.token_volumes.map((week: any) => (
              <tr key={week.week_start}>
                <td>{week.week_start}</td>
                {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map(day => (
                  <td key={day}>{formatCurrency(week.mon_volumes[day] || 0)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        <table className="w-full text-xs text-left text-gray-400">
          <thead>
            <tr>
              <th>Week Starting</th>
              <th colSpan={7}>JERRY Volume by Day</th>
            </tr>
            <tr>
              <th></th>
              {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map(day => (
                <th key={day}>{day}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {a.token_volumes.map((week: any) => (
              <tr key={week.week_start}>
                <td>{week.week_start}</td>
                {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map(day => (
                  <td key={day}>{formatCurrency(week.jerry_volumes[day] || 0)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  // User Retention Dashboard
  const renderRetentionDashboard = () => (
    <div className="bg-gray-800 p-4 rounded-lg mb-8">
      <h3 className="font-semibold text-white mb-4">User Retention (Weekly Cohorts)</h3>
      {a.retention ? (
        <>
          <table className="w-full text-xs text-left text-gray-400 mb-4">
            <thead>
              <tr>
                <th>Week Starting</th>
                <th>New Users</th>
                <th>1W</th>
                <th>2W</th>
                <th>3W</th>
                <th>4W</th>
                <th>5W</th>
                <th>6W</th>
                <th>7W</th>
                <th>8W</th>
                <th>9W</th>
                <th>10W</th>
                <th>11+W</th>
              </tr>
            </thead>
            <tbody>
              {a.retention.weeks.map((week: any) => (
                <tr key={week.earliest_date}>
                  <td>{week.earliest_date}</td>
                  <td>{formatNumber(week.new_users)}</td>
                  <td>{week.one_week_later !== undefined ? (week.one_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.two_week_later !== undefined ? (week.two_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.three_week_later !== undefined ? (week.three_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.four_week_later !== undefined ? (week.four_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.five_week_later !== undefined ? (week.five_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.six_week_later !== undefined ? (week.six_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.seven_week_later !== undefined ? (week.seven_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.eight_week_later !== undefined ? (week.eight_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.nine_week_later !== undefined ? (week.nine_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.ten_week_later !== undefined ? (week.ten_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{week.over_ten_week_later !== undefined ? (week.over_ten_week_later * 100).toFixed(1) + '%' : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="text-gray-300 text-xs">
            <b>Retention Averages:</b> 1W: {(a.retention.averages.one_week_retention * 100).toFixed(1)}% | 2W: {(a.retention.averages.two_week_retention * 100).toFixed(1)}% | 3W: {(a.retention.averages.three_week_retention * 100).toFixed(1)}% | 4W: {(a.retention.averages.four_week_retention * 100).toFixed(1)}%
          </div>
        </>
      ) : <div className="text-gray-400">Loading...</div>}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-screen-xl mx-auto p-4 md:p-6 lg:p-8">
        {/* Dashboard Header */}
        <div className="mb-8">
          <h1 className="text-4xl lg:text-5xl font-bold text-white text-center md:text-left">RBS KPI</h1>
        </div>

        {/* New Dashboards */}
        {renderTotalsDashboard()}
        {renderTokenVolumeHeatmap()}
        {renderRetentionDashboard()}
        {/* Top Bettors Table */}
        {renderTopBettors()}
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Submissions</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {formatNumber(a.total_submissions)}
            </p>
          </div>
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Active Addresses</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {formatNumber(a.active_addresses)}
            </p>
          </div>
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">$MON Volume</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {formatCurrency(a.mon_volume)}
            </p>
          </div>
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">$JERRY Volume</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {formatCurrency(a.jerry_volume)}
            </p>
          </div>
        </div>
        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          
          {/* KPI Cards */}
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Transactions</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {a.total_transactions ? formatNumber(a.total_transactions) : '0'}
            </p>
          </div>
          
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Users</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {a.total_unique_users ? formatNumber(a.total_unique_users) : '0'}
            </p>
          </div>
          
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Deposited $MON</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {a.total_mon_volume ? formatNumber(a.total_mon_volume) : '0'}
            </p>
          </div>
          
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Deposited $JERRY</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {a.total_jerry_volume ? formatNumber(a.total_jerry_volume) : '0'}
            </p>
          </div>
          
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Picked Player Cards</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {a.total_cards ? formatNumber(a.total_cards) : '0'}
            </p>
          </div>

          {/* Charts */}
          <div className="md:col-span-2 lg:col-span-3 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">New Users Over Time</h3>
            <div className="h-80">
              {a.daily_data && a.daily_data.length > 0 && (
                <Line
                  data={{
                    labels: a.daily_data.slice(-30).reverse().map((d: any) => new Date(d.date).toLocaleDateString()),
                    datasets: [
                      {
                        label: 'Daily Users',
                        data: a.daily_data.slice(-30).reverse().map((d: any) => d.active_bettors),
                        borderColor: 'rgba(99, 102, 241, 1)',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.3,
                        fill: true
                      }
                    ]
                  }}
                  options={chartOptions}
                  id="users-chart"
                />
              )}
            </div>
          </div>
          
          <div className="md:col-span-2 lg:col-span-2 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">Deposits Volume Distribution</h3>
            <div className="h-80 flex items-center justify-center">
              {a.token_stats && (
                <Pie
                  data={{
                    labels: a.token_stats.map((t: any) => `$${t.token}`),
                    datasets: [{
                      label: 'Deposit Volume',
                      data: a.token_stats.map((t: any) => t.total_volume),
                      backgroundColor: ['rgba(79, 70, 229, 0.8)', 'rgba(239, 78, 151, 0.8)'],
                      borderColor: ['#111827', '#111827'],
                      borderWidth: 2
                    }]
                  }}
                  options={pieChartOptions}
                  id="volume-chart"
                />
              )}
            </div>
          </div>
          
          <div className="md:col-span-2 lg:col-span-3 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">Total & Average Picked Player Cards Over Time</h3>
            <div className="h-80">
              {a.weekly_data && a.weekly_data.length > 0 && (
                <Bar
                  data={{
                    labels: a.weekly_data.slice(-12).map((w: any) => `Week ${w.week_number}`),
                    datasets: [
                      {
                        label: 'Total Cards',
                        data: a.weekly_data.slice(-12).map((w: any) => w.total_cards),
                        backgroundColor: 'rgba(234, 179, 8, 0.7)',
                        yAxisID: 'y'
                      },
                      {
                        label: 'Average Cards',
                        data: a.weekly_data.slice(-12).map((w: any) => w.avg_cards_per_tx),
                        borderColor: 'rgba(217, 70, 239, 1)',
                        backgroundColor: 'transparent',
                        type: 'line' as any,
                        yAxisID: 'y1'
                      }
                    ]
                  }}
                  options={{
                    ...chartOptions,
                    scales: {
                      ...chartOptions.scales,
                      y1: {
                        type: 'linear' as any,
                        display: false,
                        position: 'right' as any
                      }
                    }
                  }}
                  id="cards-chart"
                />
              )}
            </div>
          </div>
          
          <div className="md:col-span-2 lg:col-span-2 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">RBS Stats by Different Periods</h3>
            <div className="h-80 overflow-auto">
              <table className="w-full text-sm text-left text-gray-400">
                <thead className="text-xs text-gray-300 uppercase bg-gray-700/50">
                  <tr>
                    <th scope="col" className="px-4 py-3">Period</th>
                    <th scope="col" className="px-4 py-3 text-right">Txs</th>
                    <th scope="col" className="px-4 py-3 text-right">Users</th>
                  </tr>
                </thead>
                <tbody>
                  {a.period_stats.map((period: any) => (
                    <tr key={period.period} className="border-b border-gray-700">
                      <th scope="row" className="px-4 py-3 font-medium text-white whitespace-nowrap">
                        {period.period}
                      </th>
                      <td className="px-4 py-3 text-right">{formatNumber(period.transaction_count)}</td>
                      <td className="px-4 py-3 text-right">{formatNumber(period.active_bettors)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Heatmaps */}
          <div className="lg:col-span-5 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">Token Deposits Volume Heatmap by Day of Week</h3>
            <div className="overflow-x-auto">
              {createHeatmapTable(a.heatmap_data, 'total_volume')}
            </div>
          </div>
          
          <div className="lg:col-span-5 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">Bet Submission Transactions Heatmap by Day of Week</h3>
            <div className="overflow-x-auto">
              {createHeatmapTable(a.heatmap_data, 'transaction_count')}
            </div>
          </div>

          {/* Overall Stats Table */}
          <div className="lg:col-span-5 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">RBS Overall Stats Table</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-400">
                <thead className="text-xs text-gray-300 uppercase bg-gray-700/50">
                  <tr>
                    <th className="px-4 py-3">Week Starting</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3">Day of Week</th>
                    <th className="px-4 py-3">Bet Txs</th>
                    <th className="px-4 py-3">Bettors</th>
                    <th className="px-4 py-3">$MON Deposited</th>
                    <th className="px-4 py-3">$JERRY Deposited</th>
                    <th className="px-4 py-3">Avg Slip Size</th>
                    <th className="px-4 py-3">Total Cards</th>
                  </tr>
                </thead>
                <tbody>
                  {a.weekly_data.slice(-10).reverse().map((week: any) => (
                    <tr key={week.week_start} className="border-b border-gray-700">
                      <td className="px-4 py-2">{week.week_start}</td>
                      <td className="px-4 py-2">{week.week_end}</td>
                      <td className="px-4 py-2">
                        {new Date(week.week_start).toLocaleDateString('en-US', { weekday: 'long' })}
                      </td>
                      <td className="px-4 py-2">{formatNumber(week.transaction_count)}</td>
                      <td className="px-4 py-2">{formatNumber(week.active_bettors)}</td>
                      <td className="px-4 py-2">{formatNumber(week.mon_volume)}</td>
                      <td className="px-4 py-2">{formatNumber(week.jerry_volume)}</td>
                      <td className="px-4 py-2">{week.avg_cards_per_tx?.toFixed(1) ?? '-'}</td>
                      <td className="px-4 py-2">{formatNumber(week.total_cards)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 