"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { DashboardHeader } from "@/components/dashboard-header"
import { useAuth } from "@/components/auth/auth-context"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon, Trophy, Clock, Users, Hash, DollarSign } from "lucide-react"
import { format } from "date-fns"
import { cn } from "@/lib/utils"

interface RaffleResult {
  winner: {
    bet_id: number
    wallet_address: string
    entries: number
  }
  total_entries: number
  total_submissions: number
  unique_participants: number
  selection_window: {
    start_time: string
    end_time: string
    total_submissions_processed?: number
    total_cards_processed?: number
    distinct_users?: number
  }
  example_transactions: Array<{
    tx_hash: string
    timestamp: string
    token: string
    amount: number
    n_cards: number
    bet_id: number
    block_number: number
  }>
}

export default function RafflePage() {
  const { isAuthenticated } = useAuth()
  const router = useRouter()
  const [startDate, setStartDate] = useState<Date>()
  const [endDate, setEndDate] = useState<Date>()
  const [isLoading, setIsLoading] = useState(false)
  const [raffleResult, setRaffleResult] = useState<RaffleResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Redirect non-admin users
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/')
    }
  }, [isAuthenticated, router])

  const handleSelectWinner = async () => {
    if (!startDate || !endDate) {
      setError("Please select both start and end dates")
      return
    }

    if (startDate >= endDate) {
      setError("End date must be after start date")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // Environment-based API URL
      const isProduction = process.env.NODE_ENV === 'production'
      const apiUrl = isProduction 
        ? 'https://f8s8sk80ok44gw04osco04so.173.249.24.245.sslip.io'
        : 'http://localhost:8000'
      
      console.log('🎰 Attempting raffle API call...')
      const response = await fetch(`${apiUrl}/api/raffle/select-winner`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_time: startDate.toISOString(),
          end_time: endDate.toISOString(),
        }),
      })

      if (!response.ok) {
        console.log('⚠️ Raffle API failed, checking error details...')
        let errorMessage = 'Failed to select winner'
        
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          // If we can't parse error JSON, use status text
          errorMessage = `API Error: ${response.status} ${response.statusText}`
        }
        
        // For production, provide user-friendly error message
        if (isProduction) {
          setError('Raffle service is temporarily unavailable. Please try again later or contact support.')
        } else {
          setError(errorMessage)
        }
        return
      }

      const result = await response.json()
      console.log('✅ Raffle completed successfully')
      setRaffleResult(result)
    } catch (err) {
      console.error('❌ Raffle error:', err)
      
      // Network/connection errors
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Unable to connect to raffle service. Please check your connection and try again.')
      } else {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Show loading while checking authentication
  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen bg-bg-base items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-accent-primary"></div>
        <p className="ml-4 text-text-primary">Checking authentication...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-bg-base">
      <DashboardHeader />
      <main className="container mx-auto px-4 sm:px-6 py-4 sm:py-8 space-y-6 sm:space-y-8">
        {/* Main Title and Subtitle */}
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-text-primary tracking-tight mb-2">
            <Trophy className="inline w-8 h-8 text-yellow-500 mr-2" />
            RareLink Prize Raffle
          </h1>
          <p className="text-text-secondary text-sm sm:text-base leading-relaxed max-w-2xl mx-auto px-4">
            Select prize winners based on RareLink submissions within a specified time range
          </p>
        </div>

        {/* Raffle Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Raffle Configuration
            </CardTitle>
            <CardDescription>
              Set the time range for the raffle selection window
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Start Date</label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !startDate && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {startDate ? format(startDate, "PPP") : "Pick a start date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={startDate}
                      onSelect={setStartDate}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">End Date</label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !endDate && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {endDate ? format(endDate, "PPP") : "Pick an end date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={endDate}
                      onSelect={setEndDate}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
            </div>

            {error && (
              <div className="text-red-500 text-sm bg-red-50 p-2 rounded">
                {error}
              </div>
            )}

            <Button
              onClick={handleSelectWinner}
              disabled={isLoading || !startDate || !endDate}
              className="w-full"
            >
              {isLoading ? "Selecting Winner..." : "Select Winner"}
            </Button>
          </CardContent>
        </Card>

        {/* Raffle Results */}
        {raffleResult && (
          <Card className="bg-bg-elevated border-border-subtle shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-rbs-lime">
                <Trophy className="w-5 h-5" />
                Winner Selected!
              </CardTitle>
              <CardDescription className="text-text-secondary">
                Raffle completed successfully
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Winner Address - Wide Card on Top */}
              <div className="text-center p-4 bg-bg-base rounded-lg border border-border-subtle shadow-sm">
                <div className="text-lg font-bold text-rbs-lime break-all font-mono">
                  {raffleResult.winner.wallet_address}
                </div>
                <div className="text-sm text-text-secondary">Winner Address</div>
              </div>

              {/* Winner Stats */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-bg-base rounded-lg border border-border-subtle shadow-sm">
                  <div className="text-2xl font-bold text-rbs-lime">
                    {raffleResult.winner.entries}
                  </div>
                  <div className="text-sm text-text-secondary">Winner Entries</div>
                </div>
                
                <div className="text-center p-4 bg-bg-base rounded-lg border border-border-subtle shadow-sm">
                  <div className="text-2xl font-bold text-text-primary">
                    {raffleResult.total_entries.toLocaleString()}
                  </div>
                  <div className="text-sm text-text-secondary">Total Entries</div>
                </div>
                
                <div className="text-center p-4 bg-bg-base rounded-lg border border-border-subtle shadow-sm">
                  <div className="text-2xl font-bold text-text-primary">
                    {raffleResult.total_submissions.toLocaleString()}
                  </div>
                  <div className="text-sm text-text-secondary">Total Submissions</div>
                </div>
              </div>

              {/* Selection Window */}
              <div className="p-4 bg-bg-base rounded-lg border border-border-subtle shadow-sm">
                <h4 className="font-semibold mb-4 text-text-primary">Selection Window</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-text-secondary mb-2">Time Range:</div>
                    <div className="text-sm text-text-primary">
                      <div>Start: {new Date(raffleResult.selection_window.start_time).toLocaleString()}</div>
                      <div>End: {new Date(raffleResult.selection_window.end_time).toLocaleString()}</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-text-secondary mb-2">Processing Summary:</div>
                    <div className="text-sm text-text-primary space-y-1">
                      <div>Total Submissions: <span className="text-rbs-lime">{raffleResult.selection_window.total_submissions_processed?.toLocaleString() || raffleResult.total_submissions.toLocaleString()}</span></div>
                      <div>Total Cards Processed: <span className="text-rbs-lime">{raffleResult.selection_window.total_cards_processed?.toLocaleString() || 'N/A'}</span></div>
                      <div>Distinct Users: <span className="text-rbs-lime">{raffleResult.selection_window.distinct_users?.toLocaleString() || raffleResult.unique_participants.toLocaleString()}</span></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Example Transactions */}
              {raffleResult.example_transactions && raffleResult.example_transactions.length > 0 && (
                <div className="p-4 bg-bg-base rounded-lg border border-border-subtle shadow-sm">
                  <h4 className="font-semibold mb-4 text-text-primary">Winner's Recent Transactions</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border-subtle">
                          <th className="text-left py-2 text-text-primary">Transaction Hash</th>
                          <th className="text-left py-2 text-text-primary">Date</th>
                          <th className="text-left py-2 text-text-primary">Token</th>
                          <th className="text-left py-2 text-text-primary">Amount</th>
                          <th className="text-left py-2 text-text-primary">Cards</th>
                          <th className="text-left py-2 text-text-primary">Bet ID</th>
                        </tr>
                      </thead>
                      <tbody>
                        {raffleResult.example_transactions.map((tx, index) => (
                          <tr key={index} className="border-b border-border-subtle">
                            <td className="py-2 font-mono text-xs text-text-secondary">
                              {tx.tx_hash}
                            </td>
                            <td className="py-2 text-text-secondary">
                              {new Date(tx.timestamp).toLocaleString()}
                            </td>
                            <td className="py-2 text-text-secondary">{tx.token}</td>
                            <td className="py-2 text-text-secondary">{tx.amount}</td>
                            <td className="py-2 text-text-secondary">{tx.n_cards}</td>
                            <td className="py-2 text-text-secondary">{tx.bet_id}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
} 