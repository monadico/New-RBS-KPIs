// components/rbs-tables/cohort-retention-table.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { formatNumber } from "@/lib/utils"
import { Users, TrendingUp } from "lucide-react"

interface CohortRetentionData {
  earliest_date: string
  users: number
  retention_weeks: {
    [key: string]: {
      users: number
      percentage: number
    }
  }
}

interface CohortRetentionTableProps {
  data: CohortRetentionData[]
}

export function CohortRetentionTable({ data }: CohortRetentionTableProps) {
  if (!data || data.length === 0) {
    return (
      <Card className="bg-surface border-border-subtle shadow-card-medium">
        <CardContent className="p-6">
          <div className="text-center text-text-secondary">
            No cohort retention data available
          </div>
        </CardContent>
      </Card>
    )
  }

  // Generate week headers (1 week later to 10 weeks later, then 11+ weeks later)
  const weekHeaders = []
  for (let i = 1; i <= 10; i++) {
    weekHeaders.push(`${i} week${i > 1 ? 's' : ''} later`)
  }
  weekHeaders.push('11+ weeks later')

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium hover:shadow-card-elevated transition-all duration-500 group">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500/10 rounded-lg border border-green-500/20">
                <TrendingUp className="w-4 h-4 text-green-400" />
              </div>
              <CardTitle className="text-xl font-bold text-text-primary tracking-tight">
                RBS User Weekly Cohort Retention
              </CardTitle>
            </div>
            <CardDescription className="text-text-secondary text-sm leading-relaxed">
              Weekly retention analysis showing user engagement over time
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider w-16">
                #
              </TableHead>
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider">
                Earliest week (starting date)
              </TableHead>
              <TableHead className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right">
                User count
              </TableHead>
              {weekHeaders.map((header, index) => (
                <TableHead 
                  key={index}
                  className="text-text-tertiary text-xs font-medium uppercase tracking-wider text-right"
                >
                  {header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((cohort, index) => (
              <TableRow
                key={cohort.earliest_date}
                className="hover:bg-surface-elevated transition-colors duration-200 border-border-subtle"
              >
                <TableCell className="text-text-secondary font-medium">
                  {index + 1}
                </TableCell>
                <TableCell className="font-medium text-text-primary">
                  {cohort.earliest_date}
                </TableCell>
                <TableCell className="text-right text-text-secondary font-semibold">
                  {formatNumber(cohort.users)}
                </TableCell>
                {weekHeaders.map((header, weekIndex) => {
                  const weekKey = weekIndex < 10 
                    ? `${weekIndex + 1}_week_later` 
                    : 'over_ten_week_later'
                  
                  const retentionData = cohort.retention_weeks[weekKey]
                  const percentage = retentionData?.percentage || 0
                  
                  return (
                    <TableCell 
                      key={weekIndex}
                      className="text-right text-text-secondary"
                    >
                      {percentage > 0 ? `${percentage.toFixed(2)}%` : '-'}
                    </TableCell>
                  )
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
} 