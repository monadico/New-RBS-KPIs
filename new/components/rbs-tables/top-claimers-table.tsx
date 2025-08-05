// components/rbs-tables/top-claimers-table.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { TopClaimer } from "@/lib/data-types"
import { formatCurrency, formatNumber, formatAddress, cn } from "@/lib/utils"
import { Crown, TrendingUp, TrendingDown } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface TopClaimersTableProps {
  data: TopClaimer[]
}

export function TopClaimersTable({ data }: TopClaimersTableProps) {
  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group lg:col-span-full">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500/10 rounded-lg border border-green-500/20">
                <TrendingUp className="w-4 h-4 text-green-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">Top 20 Claimers</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Leading claimers by total claimed amount and profit performance.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <TooltipProvider>
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider">Rank</TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider">
                  Address
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Total Claimed
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  MON Claimed
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  JERRY Claimed
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Total Claims
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Total Bet
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Profit %
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Submissions
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Avg Slip Size
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((claimer, index) => (
                <TableRow
                  key={claimer.address}
                  className={cn(
                    "hover:bg-surface-elevated transition-colors duration-200 border-border-subtle",
                    index === 0 && "bg-rbs-lime/10 hover:bg-rbs-lime/20", // Gold - Arctic Lime
                    index === 1 && "bg-rbs-accent/10 hover:bg-rbs-accent/20", // Silver - Accent
                    index === 2 && "bg-rbs-dark-lime/10 hover:bg-rbs-dark-lime/20", // Bronze - Dark Lime
                  )}
                >
                  <TableCell className="font-bold text-text-primary">
                    {claimer.rank}
                    {index === 0 && <Crown className="inline-block w-4 h-4 ml-1 text-rbs-lime fill-rbs-lime/20" />}
                  </TableCell>
                  <TableCell className="font-mono text-text-mono">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span>{claimer.display_address}</span>
                      </TooltipTrigger>
                      <TooltipContent className="bg-bg-elevated border-border-medium text-text-primary">
                        {claimer.address}
                      </TooltipContent>
                    </Tooltip>
                  </TableCell>
                  <TableCell className="text-right text-text-primary font-semibold">
                    {formatCurrency(claimer.total_claimed)}
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">
                    {formatCurrency(claimer.mon_claimed)}
                    <div className="text-xs text-text-tertiary">
                      ({claimer.mon_percentage}%)
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">
                    {formatCurrency(claimer.jerry_claimed)}
                    <div className="text-xs text-text-tertiary">
                      ({claimer.jerry_percentage}%)
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">
                    {formatNumber(claimer.total_claims)}
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">
                    {formatCurrency(claimer.total_bet)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className={cn(
                      "font-semibold",
                      claimer.profit_percentage > 0 ? "text-green-500" : 
                      claimer.profit_percentage < 0 ? "text-red-500" : "text-text-secondary"
                    )}>
                      {claimer.profit_percentage > 0 ? "+" : ""}{claimer.profit_percentage.toFixed(1)}%
                      {claimer.profit_percentage > 0 && <TrendingUp className="inline-block w-3 h-3 ml-1" />}
                      {claimer.profit_percentage < 0 && <TrendingDown className="inline-block w-3 h-3 ml-1" />}
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">
                    {formatNumber(claimer.total_submissions)}
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">
                    {claimer.avg_slip_size.toFixed(1)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TooltipProvider>
      </CardContent>
    </Card>
  )
} 