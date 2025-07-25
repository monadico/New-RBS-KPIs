// components/rbs-tables/rbs-daily-stats-table.tsx
"use client"

import { useState, useMemo } from "react"
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ChevronDown, ChevronUp, ChevronsUpDown, Search, Download } from "lucide-react"
import type { PeriodData } from "@/lib/data-types"
import { formatCurrency, formatNumber } from "@/lib/utils"

interface RbsDailyStatsTableProps {
  data: PeriodData[]
}

// Define the extended data type with computed fields
interface ExtendedPeriodData extends PeriodData {
  dayOfWeek: string
  averageSlipSize: number
  correctedDate: Date
}

export function RbsDailyStatsTable({ data }: RbsDailyStatsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [globalFilter, setGlobalFilter] = useState("")

  // Transform data to include day of week, average slip size, and corrected date
  const transformedData = useMemo<ExtendedPeriodData[]>(() => {
    return data.map((period) => {
      // Parse date as local time to avoid timezone issues
      const [year, month, day] = period.start_date.split('-').map(Number)
      const date = new Date(year, month - 1, day) // month is 0-indexed
      const dayOfWeek = date.toLocaleDateString('en-US', { weekday: 'long' })
      const averageSlipSize = period.submissions > 0 ? period.total_cards / period.submissions : 0
      
      return {
        ...period,
        dayOfWeek,
        averageSlipSize,
        // Store the corrected date for sorting
        correctedDate: date,
      }
    })
  }, [data])

  const columns = useMemo<ColumnDef<ExtendedPeriodData>[]>(
    () => [
      {
        accessorKey: "start_date",
        header: "Date",
        cell: ({ getValue }) => {
          const value = getValue() as string
          // Parse date as local time to avoid timezone issues
          const [year, month, day] = value.split('-').map(Number)
          const date = new Date(year, month - 1, day)
          return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit' 
          })
        },
        sortingFn: "datetime",
      },
      {
        accessorKey: "dayOfWeek",
        header: "Day of Week",
        cell: ({ getValue }) => getValue() as string,
      },
      {
        accessorKey: "submissions",
        header: "Submissions",
        cell: ({ getValue }) => formatNumber(getValue() as number),
        sortingFn: "basic",
      },
      {
        accessorKey: "active_addresses",
        header: "Distinct Bettors",
        cell: ({ getValue }) => formatNumber(getValue() as number),
        sortingFn: "basic",
      },
      {
        accessorKey: "mon_volume",
        header: "MON Deposited",
        cell: ({ getValue }) => formatCurrency(getValue() as number),
        sortingFn: "basic",
      },
      {
        accessorKey: "jerry_volume",
        header: "JERRY Deposited",
        cell: ({ getValue }) => formatCurrency(getValue() as number),
        sortingFn: "basic",
      },
      {
        accessorKey: "averageSlipSize",
        header: "Avg Slip Size",
        cell: ({ getValue }) => formatNumber(getValue() as number),
        sortingFn: "basic",
      },
      {
        accessorKey: "total_cards",
        header: "Total Cards",
        cell: ({ getValue }) => formatNumber(getValue() as number),
        sortingFn: "basic",
      },
    ],
    []
  )

  const table = useReactTable({
    data: transformedData,
    columns,
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 20,
      },
    },
  })

  const getSortIcon = (column: any) => {
    if (!column.getCanSort()) return null
    
    const isSorted = column.getIsSorted()
    if (isSorted === "asc") return <ChevronUp className="h-4 w-4" />
    if (isSorted === "desc") return <ChevronDown className="h-4 w-4" />
    return <ChevronsUpDown className="h-4 w-4" />
  }

  const exportToCSV = () => {
    const headers = columns.map(col => col.header as string).join(",")
    const rows = transformedData.map(row => 
      [
        row.correctedDate.toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: '2-digit', 
          day: '2-digit' 
        }),
        row.dayOfWeek,
        row.submissions,
        row.active_addresses,
        row.mon_volume,
        row.jerry_volume,
        row.averageSlipSize,
        row.total_cards
      ].join(",")
    ).join("\n")
    
    const csv = `${headers}\n${rows}`
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rbs-daily-stats-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <Card className="bg-surface border-border-subtle shadow-card-medium">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl font-bold text-text-primary">
              RBS Daily Statistics
            </CardTitle>
            <CardDescription className="text-text-secondary">
              Daily performance metrics since platform launch
            </CardDescription>
          </div>
          <Button
            onClick={exportToCSV}
            variant="outline"
            size="sm"
            className="bg-surface-elevated hover:bg-surface border-border-subtle"
          >
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Search and Controls */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Search className="h-4 w-4 text-text-secondary" />
            <Input
              placeholder="Search all columns..."
              value={globalFilter ?? ""}
              onChange={(event) => setGlobalFilter(event.target.value)}
              className="w-64 bg-surface-elevated border-border-subtle"
            />
          </div>
          <div className="text-sm text-text-secondary">
            Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{" "}
            {Math.min(
              (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
              table.getFilteredRowModel().rows.length
            )}{" "}
            of {table.getFilteredRowModel().rows.length} results
          </div>
        </div>

        {/* Table */}
        <div className="rounded-lg border border-border-subtle overflow-hidden">
          <Table>
            <TableHeader className="bg-surface-elevated">
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead
                      key={header.id}
                      className={`text-text-primary font-semibold ${
                        header.column.getCanSort() ? "cursor-pointer select-none hover:bg-surface" : ""
                      }`}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      <div className="flex items-center gap-2">
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {getSortIcon(header.column)}
                      </div>
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    className="hover:bg-surface-elevated transition-colors"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id} className="text-text-primary">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={columns.length} className="h-24 text-center text-text-secondary">
                    No results found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.setPageIndex(0)}
              disabled={!table.getCanPreviousPage()}
              className="bg-surface-elevated hover:bg-surface border-border-subtle"
            >
              First
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="bg-surface-elevated hover:bg-surface border-border-subtle"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="bg-surface-elevated hover:bg-surface border-border-subtle"
            >
              Next
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.setPageIndex(table.getPageCount() - 1)}
              disabled={!table.getCanNextPage()}
              className="bg-surface-elevated hover:bg-surface border-border-subtle"
            >
              Last
            </Button>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-text-secondary">Page</span>
            <strong className="text-text-primary">
              {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
            </strong>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 