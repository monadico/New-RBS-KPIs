// lib/mock-data.ts
import type {
  AnalyticsData,
  TimeframeData,
  PeriodData,
  PlayerCategory,
  SlipCardCount,
  TopBettor,
  RbsStatsPeriod,
} from "./data-types"

const generateRandomNumber = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min
const generateRandomDecimal = (min: number, max: number, fixed = 1) =>
  (Math.random() * (max - min) + min).toFixed(fixed)

const formatDate = (date: Date) => date.toISOString().split("T")[0]

const generatePeriodData = (numPeriods: number, startDate: Date, interval: "day" | "week" | "month"): PeriodData[] => {
  const data: PeriodData[] = []
  let currentCumulativeBettors = 1000 // Starting point for cumulative bettors

  for (let i = 0; i < numPeriods; i++) {
    const periodStartDate = new Date(startDate)
    if (interval === "day") periodStartDate.setDate(startDate.getDate() + i)
    else if (interval === "week") periodStartDate.setDate(startDate.getDate() + i * 7)
    else if (interval === "month") periodStartDate.setMonth(startDate.getMonth() + i)

    const submissions = generateRandomNumber(500, 2000)
    const activeAddresses = generateRandomNumber(200, 1000)
    const newBettors = generateRandomNumber(20, 150)
    const monVolume = generateRandomNumber(10000, 50000)
    const jerryVolume = generateRandomNumber(5000, 25000)
    const totalCards = generateRandomNumber(1000, 4000)
    const avgCardsPerSubmission = Number.parseFloat(generateRandomDecimal(1.5, 4.5))

    currentCumulativeBettors += newBettors // Update cumulative bettors

    data.push({
      period: i + 1,
      start_date: formatDate(periodStartDate),
      end_date: formatDate(
        new Date(
          periodStartDate.getTime() +
            (interval === "day"
              ? 24 * 60 * 60 * 1000
              : interval === "week"
                ? 7 * 24 * 60 * 60 * 1000
                : 30 * 24 * 60 * 60 * 1000),
        ),
      ), // Simplified end date
      submissions,
      active_addresses: activeAddresses,
      new_bettors: newBettors,
      mon_volume: monVolume,
      jerry_volume: jerryVolume,
      total_volume: monVolume + jerryVolume,
      total_cards: totalCards,
      avg_cards_per_submission: avgCardsPerSubmission,
      cumulative_bettors: currentCumulativeBettors, // Add cumulative bettors here
    } as PeriodData & { cumulative_bettors: number }) // Type assertion for now
  }
  return data
}

const generatePlayerActivity = (): { categories: PlayerCategory[]; total_players: number } => {
  const categories: PlayerCategory[] = [
    { category: "High Rollers", player_count: generateRandomNumber(50, 150), percentage: 0 },
    { category: "Frequent Bettors", player_count: generateRandomNumber(200, 400), percentage: 0 },
    { category: "Casual Players", player_count: generateRandomNumber(500, 800), percentage: 0 },
    { category: "New Users", player_count: generateRandomNumber(100, 250), percentage: 0 },
  ]
  const totalPlayers = categories.reduce((sum, cat) => sum + cat.player_count, 0)
  categories.forEach(
    (cat) => (cat.percentage = Number.parseFloat(((cat.player_count / totalPlayers) * 100).toFixed(1))),
  )
  return { categories, total_players: totalPlayers }
}

const generateOverallSlipsByCardCount = (): SlipCardCount[] => {
  const data: SlipCardCount[] = []
  const totalBets = generateRandomNumber(5000, 10000)
  for (let i = 2; i <= 7; i++) {
    const bets = generateRandomNumber(totalBets / 10, totalBets / 4)
    data.push({ cards_in_slip: i, bets, percentage: 0 })
  }
  const currentTotalBets = data.reduce((sum, item) => sum + item.bets, 0)
  data.forEach((item) => (item.percentage = Number.parseFloat(((item.bets / currentTotalBets) * 100).toFixed(1))))
  return data
}

const generateTopBettors = (): TopBettor[] => {
  const bettors: TopBettor[] = []
  for (let i = 1; i <= 20; i++) {
    bettors.push({
      user_address: `0x${Math.random().toString(16).substring(2, 42)}`,
      rank: i,
      total_mon: generateRandomNumber(10000, 100000),
      total_jerry: generateRandomNumber(5000, 50000),
      total_bets: generateRandomNumber(50, 500),
      avg_cards_per_slip: Number.parseFloat(generateRandomDecimal(2.0, 5.0)),
      active_days: generateRandomNumber(10, 90),
    })
  }
  return bettors.sort((a, b) => b.total_mon + b.total_jerry - (a.total_mon + a.total_jerry))
}

const generateRbsStatsByPeriods = (numPeriods: number, interval: "day" | "week" | "month"): RbsStatsPeriod[] => {
  const data: RbsStatsPeriod[] = []
  for (let i = 0; i < numPeriods; i++) {
    const monVolume = generateRandomNumber(50000, 200000)
    const jerryVolume = generateRandomNumber(20000, 100000)
    const submissions = generateRandomNumber(1000, 5000)
    const activeBettors = generateRandomNumber(500, 2000)
    const totalCards = generateRandomNumber(3000, 10000)
    data.push({
      period: `${interval === "day" ? "Day" : interval === "week" ? "Week" : "Month"} ${i + 1}`,
      mon_volume: monVolume,
      jerry_volume: jerryVolume,
      total_volume: monVolume + jerryVolume,
      submissions,
      active_bettors: activeBettors,
      total_cards: totalCards,
    })
  }
  return data
}

const generateAnalyticsData = (timeframe: "daily" | "weekly" | "monthly"): AnalyticsData => {
  const numPeriods = timeframe === "daily" ? 30 : timeframe === "weekly" ? 12 : 6
  const startDate = new Date(2024, 0, 1) // Jan 1, 2024

  const totalSubmissions = generateRandomNumber(50000, 200000)
  const totalActiveAddresses = generateRandomNumber(10000, 50000)
  const totalMonVolume = generateRandomNumber(1000000, 5000000)
  const totalJerryVolume = generateRandomNumber(500000, 2500000)
  const totalCards = generateRandomNumber(200000, 800000)

  return {
    timeframe: timeframe,
    start_date: formatDate(startDate),
    total_periods: numPeriods,
    total_metrics: {
      total_submissions: totalSubmissions,
      total_active_addresses: totalActiveAddresses,
      total_mon_volume: totalMonVolume,
      total_jerry_volume: totalJerryVolume,
      total_cards: totalCards,
    },
    average_metrics: {
      avg_submissions_per_day: Number.parseFloat(generateRandomDecimal(100, 500)),
      avg_players_per_day: Number.parseFloat(generateRandomDecimal(50, 200)),
      avg_cards_per_slip: Number.parseFloat(generateRandomDecimal(2.0, 4.0)),
    },
    activity_over_time: generatePeriodData(
      numPeriods,
      startDate,
      timeframe === "daily" ? "day" : timeframe === "weekly" ? "week" : "month",
    ),
    player_activity: generatePlayerActivity(),
    overall_slips_by_card_count: generateOverallSlipsByCardCount(),
    top_bettors: generateTopBettors(),
    rbs_stats_by_periods: generateRbsStatsByPeriods(
      numPeriods,
      timeframe === "daily" ? "day" : timeframe === "weekly" ? "week" : "month",
    ),
  }
}

export const mockAnalyticsData: TimeframeData = {
  daily: generateAnalyticsData("daily"),
  weekly: generateAnalyticsData("weekly"),
  monthly: generateAnalyticsData("monthly"),
}
