import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import type { BidOpportunity, BidScore, ScoredBid } from '@/types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Format currency
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

// Format date
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(d)
}

// Format relative time
export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffMs = d.getTime() - now.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays < 0) return 'Closed'
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Tomorrow'
  if (diffDays < 7) return `in ${diffDays} days`
  if (diffDays < 30) return `in ${Math.floor(diffDays / 7)} weeks`
  return `in ${Math.floor(diffDays / 30)} months`
}

// Get tier badge color
export function getTierColor(tier: 'priority' | 'review' | 'low'): string {
  switch (tier) {
    case 'priority':
      return 'bg-green-100 text-green-800 border-green-200'
    case 'review':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    case 'low':
      return 'bg-red-100 text-red-800 border-red-200'
  }
}

// Get tier label
export function getTierLabel(tier: 'priority' | 'review' | 'low'): string {
  switch (tier) {
    case 'priority':
      return 'Priority'
    case 'review':
      return 'Review'
    case 'low':
      return 'Low'
  }
}

// Export bids to CSV
export function exportToCSV(bids: ScoredBid[], filename: string = 'pursuit_list.csv') {
  const headers = [
    'Score',
    'Tier',
    'Title',
    'Agency',
    'Budget',
    'Category',
    'Location',
    'Closing Date',
    'Delivery Days',
    'URL'
  ]

  const rows = bids.map(bid => [
    bid.score?.totalScore || 0,
    bid.score?.tier || 'N/A',
    bid.title,
    bid.procuringEntity,
    bid.budget,
    bid.category,
    bid.areaOfDelivery,
    formatDate(bid.closingDate),
    bid.deliveryDays,
    bid.sourceUrl || ''
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map(row =>
      row.map(cell =>
        typeof cell === 'string' && cell.includes(',')
          ? `"${cell}"`
          : cell
      ).join(',')
    )
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Generate unique ID
export function generateId(prefix: string = 'id'): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}
