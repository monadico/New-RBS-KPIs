// components/rbs-tables/top-bettors-table.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { TopBettor } from "@/lib/data-types"
import { formatCurrency, formatNumber, formatAddress, cn } from "@/lib/utils"
import { Crown } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface TopBettorsTableProps {
  data: TopBettor[]
}

export function TopBettorsTable({ data }: TopBettorsTableProps) {
  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group lg:col-span-full">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                <Crown className="w-4 h-4 text-yellow-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">Top 20 Bettors</CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Leading bettors by total volume and activity.
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
                  Total MON
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Total JERRY
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Total Bets
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Avg Cards/Slip
                </TableHead>
                <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                  Active Days
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((bettor, index) => (
                <TableRow
                  key={bettor.user_address}
                  className={cn(
                    "hover:bg-surface-elevated transition-colors duration-200 border-border-subtle",
                    index === 0 && "bg-rbs-lime/10 hover:bg-rbs-lime/20", // Gold - Arctic Lime
                    index === 1 && "bg-rbs-accent/10 hover:bg-rbs-accent/20", // Silver - Accent
                    index === 2 && "bg-rbs-dark-lime/10 hover:bg-rbs-dark-lime/20", // Bronze - Dark Lime
                  )}
                >
                  <TableCell className="font-bold text-text-primary">
                    {bettor.rank}
                    {index === 0 && <Crown className="inline-block w-4 h-4 ml-1 text-rbs-lime fill-rbs-lime/20" />}
                  </TableCell>
                  <TableCell className="font-mono text-text-mono">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span>{formatAddress(bettor.user_address)}</span>
                      </TooltipTrigger>
                      <TooltipContent className="bg-bg-elevated border-border-medium text-text-primary">
                        {bettor.user_address}
                      </TooltipContent>
                    </Tooltip>
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">{formatCurrency(bettor.total_mon)}</TableCell>
                  <TableCell className="text-right text-text-secondary">{formatCurrency(bettor.total_jerry)}</TableCell>
                  <TableCell className="text-right text-text-primary font-semibold">
                    {formatNumber(bettor.total_bets)}
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">
                    {bettor.avg_cards_per_slip.toFixed(1)}
                  </TableCell>
                  <TableCell className="text-right text-text-secondary">{bettor.active_days}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TooltipProvider>
      </CardContent>
    </Card>
  )
}
