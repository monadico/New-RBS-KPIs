// components/rbs-tables/rbs-periods-table.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { formatCurrency, formatNumber } from "@/lib/utils"
import { BarChart3 } from "lucide-react"

interface RbsPeriodsTableProps {
  data: Array<{
    period: string
    mon_volume: number
    jerry_volume: number
    total_volume: number
    submissions: number
    active_bettors: number
    total_cards: number
  }>
}

export function RbsPeriodsTable({ data }: RbsPeriodsTableProps) {
  if (!data || data.length === 0) {
    return (
      <Card className="bg-surface border-border-subtle shadow-card-medium">
        <CardContent className="p-6">
          <div className="text-center text-text-secondary">
            No period data available
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <BarChart3 className="w-4 h-4 text-blue-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">
                RBS Stats by Periods
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Aggregated performance metrics for different time periods
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider">Period</TableHead>
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                MON Volume
              </TableHead>
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                JERRY Volume
              </TableHead>
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                Total Volume
              </TableHead>
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                Submissions
              </TableHead>
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                Active Bettors
              </TableHead>
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                Total Cards
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, index) => (
              <TableRow
                key={index}
                className="hover:bg-surface-elevated transition-colors duration-200 border-border-subtle"
              >
                <TableCell className="font-medium text-text-primary">
                  {row.period}
                </TableCell>
                <TableCell className="text-right text-text-secondary">
                  {formatCurrency(row.mon_volume)}
                </TableCell>
                <TableCell className="text-right text-text-secondary">
                  {formatCurrency(row.jerry_volume)}
                </TableCell>
                <TableCell className="text-right text-text-primary font-semibold">
                  {formatCurrency(row.total_volume)}
                </TableCell>
                <TableCell className="text-right text-text-secondary">
                  {formatNumber(row.submissions)}
                </TableCell>
                <TableCell className="text-right text-text-secondary">
                  {formatNumber(row.active_bettors)}
                </TableCell>
                <TableCell className="text-right text-text-secondary">
                  {formatNumber(row.total_cards)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
} 