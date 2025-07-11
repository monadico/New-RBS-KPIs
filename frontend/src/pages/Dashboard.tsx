import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { DashboardStats, WeeklyData, DailyData, HeatmapData, PeriodStats } from '../types';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [weeklyData, setWeeklyData] = useState<WeeklyData[]>([]);
  const [dailyData, setDailyData] = useState<DailyData[]>([]);
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const [periodStats, setPeriodStats] = useState<PeriodStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch all data in parallel
      const [statsRes, weeklyRes, dailyRes, heatmapRes, periodsRes] = await Promise.all([
        fetch('/api/stats'),
        fetch('/api/weekly'),
        fetch('/api/daily'),
        fetch('/api/heatmap'),
        fetch('/api/periods')
      ]);

      const [statsData, weeklyData, dailyData, heatmapData, periodsData] = await Promise.all([
        statsRes.json(),
        weeklyRes.json(),
        dailyRes.json(),
        heatmapRes.json(),
        periodsRes.json()
      ]);

      if (statsData.success) {
        setStats(statsData.data);
      }

      if (weeklyData.success) {
        setWeeklyData(weeklyData.data.weeks);
      }

      if (dailyData.success) {
        setDailyData(dailyData.data);
      }

      if (heatmapData.success) {
        setHeatmapData(heatmapData.data);
      }

      if (periodsData.success) {
        setPeriodStats(periodsData.data);
      }

    } catch (err) {
      setError('Failed to fetch data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number): string => {
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

  const createHeatmapTable = (data: HeatmapData[], metric: 'transaction_count' | 'unique_users' | 'total_volume') => {
    const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const maxValue = Math.max(...data.map(d => d[metric]));
    
    return (
      <table className="w-full text-sm">
        <thead>
          <tr className="text-gray-400 border-b border-gray-700">
            <th className="text-left py-2">Day</th>
            <th className="text-right py-2">Value</th>
            <th className="text-right py-2">Percentage</th>
          </tr>
        </thead>
        <tbody>
          {dayNames.map((day, index) => {
            const dayData = data.find(d => d.day_of_week === index);
            const value = dayData ? dayData[metric] : 0;
            const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
            const intensity = percentage / 100;
            
            return (
              <tr key={day} className="border-b border-gray-700">
                <td className="py-2 text-white">{day}</td>
                <td className="py-2 text-right text-white">
                  {metric === 'total_volume' ? formatCurrency(value) : formatNumber(value)}
                </td>
                <td className="py-2 text-right">
                  <div className="flex items-center justify-end">
                    <div 
                      className="w-16 h-2 bg-gray-700 rounded mr-2"
                      style={{
                        background: `linear-gradient(to right, rgba(79, 70, 229, ${intensity * 0.8 + 0.1}), rgba(79, 70, 229, ${intensity * 0.8 + 0.1}))`
                      }}
                    />
                    <span className="text-gray-400 text-xs">{percentage.toFixed(1)}%</span>
                  </div>
                </td>
              </tr>
            );
          })}
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

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="max-w-screen-xl mx-auto p-4 md:p-6 lg:p-8">
        {/* Dashboard Header */}
        <div className="mb-8">
          <h1 className="text-4xl lg:text-5xl font-bold text-white text-center md:text-left">RBS KPI</h1>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          
          {/* KPI Cards */}
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Transactions</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {stats ? formatNumber(stats.total_transactions) : '0'}
            </p>
          </div>
          
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Users</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {stats ? formatNumber(stats.unique_users) : '0'}
            </p>
          </div>
          
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Deposited $MON</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {stats ? formatNumber(stats.token_stats.find(t => t.token === 'MON')?.total_volume || 0) : '0'}
            </p>
          </div>
          
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Deposited $JERRY</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {stats ? formatNumber(stats.token_stats.find(t => t.token === 'Jerry')?.total_volume || 0) : '0'}
            </p>
          </div>
          
          <div className="bg-gray-800 p-5 rounded-lg flex flex-col justify-center items-center text-center">
            <h3 className="text-base font-medium text-gray-400">Total Picked Player Cards</h3>
            <p className="text-4xl font-bold text-indigo-400 mt-2">
              {stats ? formatNumber(stats.total_cards) : '0'}
            </p>
          </div>

          {/* Charts */}
          <div className="md:col-span-2 lg:col-span-3 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">New Users Over Time</h3>
            <div className="h-80">
              {dailyData.length > 0 && (
                <Line
                  data={{
                    labels: dailyData.slice(-30).map(d => new Date(d.date).toLocaleDateString()),
                    datasets: [
                      {
                        label: 'Daily Users',
                        data: dailyData.slice(-30).map(d => d.unique_users),
                        borderColor: 'rgba(99, 102, 241, 1)',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.3,
                        fill: true
                      }
                    ]
                  }}
                  options={chartOptions}
                />
              )}
            </div>
          </div>
          
          <div className="md:col-span-2 lg:col-span-2 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">Deposits Volume Distribution</h3>
            <div className="h-80 flex items-center justify-center">
              {stats && (
                <Pie
                  data={{
                    labels: stats.token_stats.map(t => `$${t.token}`),
                    datasets: [{
                      label: 'Deposit Volume',
                      data: stats.token_stats.map(t => t.total_volume),
                      backgroundColor: ['rgba(79, 70, 229, 0.8)', 'rgba(239, 78, 151, 0.8)'],
                      borderColor: ['#111827', '#111827'],
                      borderWidth: 2
                    }]
                  }}
                  options={pieChartOptions}
                />
              )}
            </div>
          </div>
          
          <div className="md:col-span-2 lg:col-span-3 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">Total & Average Picked Player Cards Over Time</h3>
            <div className="h-80">
              {weeklyData.length > 0 && (
                <Bar
                  data={{
                    labels: weeklyData.slice(-12).map(w => `Week ${w.week_number}`),
                    datasets: [
                      {
                        label: 'Total Cards',
                        data: weeklyData.slice(-12).map(w => w.total_cards),
                        backgroundColor: 'rgba(234, 179, 8, 0.7)',
                        yAxisID: 'y'
                      },
                      {
                        label: 'Average Cards',
                        data: weeklyData.slice(-12).map(w => w.avg_cards),
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
                  {periodStats.map((period) => (
                    <tr key={period.period} className="border-b border-gray-700">
                      <th scope="row" className="px-4 py-3 font-medium text-white whitespace-nowrap">
                        {period.period}
                      </th>
                      <td className="px-4 py-3 text-right">{formatNumber(period.transactions)}</td>
                      <td className="px-4 py-3 text-right">{formatNumber(period.users)}</td>
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
              {createHeatmapTable(heatmapData, 'total_volume')}
            </div>
          </div>
          
          <div className="lg:col-span-5 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">Bet Submission Transactions Heatmap by Day of Week</h3>
            <div className="overflow-x-auto">
              {createHeatmapTable(heatmapData, 'transaction_count')}
            </div>
          </div>
          
          <div className="lg:col-span-5 bg-gray-800 p-4 rounded-lg">
            <h3 className="font-semibold text-white mb-4">User Activity Heatmap by Day of Week</h3>
            <div className="overflow-x-auto">
              {createHeatmapTable(heatmapData, 'unique_users')}
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
                  {weeklyData.slice(-10).reverse().map((week) => (
                    <tr key={week.week_start} className="border-b border-gray-700">
                      <td className="px-4 py-2">{week.week_start}</td>
                      <td className="px-4 py-2">{week.week_end}</td>
                      <td className="px-4 py-2">
                        {new Date(week.week_start).toLocaleDateString('en-US', { weekday: 'long' })}
                      </td>
                      <td className="px-4 py-2">{formatNumber(week.transaction_count)}</td>
                      <td className="px-4 py-2">{formatNumber(week.unique_users)}</td>
                      <td className="px-4 py-2">{formatNumber(week.mon_volume)}</td>
                      <td className="px-4 py-2">{formatNumber(week.jerry_volume)}</td>
                      <td className="px-4 py-2">{week.avg_cards.toFixed(1)}</td>
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