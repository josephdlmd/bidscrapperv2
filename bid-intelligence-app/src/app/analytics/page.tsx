'use client'

import { useEffect, useState } from 'react'
import { TrendingUp, Award, Target, DollarSign } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { getBids, getScores, getDecisions } from '@/lib/storage/localStorage'
import { formatCurrency } from '@/lib/utils'

export default function AnalyticsPage() {
  const [stats, setStats] = useState({
    totalBids: 0,
    averageScore: 0,
    totalValue: 0,
    pursuedValue: 0,
    categoryBreakdown: {} as Record<string, number>,
    locationBreakdown: {} as Record<string, number>,
    tierBreakdown: { priority: 0, review: 0, low: 0 },
    decisionRate: { pursue: 0, pass: 0, pending: 0 }
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const bids = getBids()
    const scores = getScores()
    const decisions = getDecisions()

    // Calculate stats
    const totalBids = bids.length
    const averageScore = scores.length > 0
      ? scores.reduce((sum, s) => sum + s.totalScore, 0) / scores.length
      : 0

    const totalValue = bids.reduce((sum, b) => sum + b.budget, 0)

    const pursuedBidIds = decisions
      .filter(d => d.decision === 'pursue')
      .map(d => d.bidId)
    const pursuedValue = bids
      .filter(b => pursuedBidIds.includes(b.id))
      .reduce((sum, b) => sum + b.budget, 0)

    // Category breakdown
    const categoryBreakdown: Record<string, number> = {}
    bids.forEach(bid => {
      categoryBreakdown[bid.category] = (categoryBreakdown[bid.category] || 0) + 1
    })

    // Location breakdown
    const locationBreakdown: Record<string, number> = {}
    bids.forEach(bid => {
      locationBreakdown[bid.areaOfDelivery] = (locationBreakdown[bid.areaOfDelivery] || 0) + 1
    })

    // Tier breakdown
    const tierBreakdown = {
      priority: scores.filter(s => s.tier === 'priority').length,
      review: scores.filter(s => s.tier === 'review').length,
      low: scores.filter(s => s.tier === 'low').length
    }

    // Decision rate
    const decisionRate = {
      pursue: decisions.filter(d => d.decision === 'pursue').length,
      pass: decisions.filter(d => d.decision === 'pass').length,
      pending: totalBids - decisions.length
    }

    setStats({
      totalBids,
      averageScore,
      totalValue,
      pursuedValue,
      categoryBreakdown,
      locationBreakdown,
      tierBreakdown,
      decisionRate
    })

    setLoading(false)
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  const topCategories = Object.entries(stats.categoryBreakdown)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5)

  const topLocations = Object.entries(stats.locationBreakdown)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-gray-600">Performance insights and bid statistics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Opportunities</p>
              <p className="text-3xl font-bold mt-1">{stats.totalBids}</p>
            </div>
            <Target className="h-10 w-10 text-blue-400" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Average Score</p>
              <p className="text-3xl font-bold mt-1">{stats.averageScore.toFixed(0)}</p>
            </div>
            <Award className="h-10 w-10 text-green-400" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Value</p>
              <p className="text-2xl font-bold mt-1">{formatCurrency(stats.totalValue)}</p>
            </div>
            <DollarSign className="h-10 w-10 text-yellow-400" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pursued Value</p>
              <p className="text-2xl font-bold mt-1">{formatCurrency(stats.pursuedValue)}</p>
            </div>
            <TrendingUp className="h-10 w-10 text-purple-400" />
          </div>
        </Card>
      </div>

      {/* Charts and Breakdowns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Score Distribution */}
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Score Distribution</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Priority (≥75)</span>
                <span className="font-semibold text-green-600">{stats.tierBreakdown.priority}</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-500"
                  style={{
                    width: `${(stats.tierBreakdown.priority / stats.totalBids) * 100}%`
                  }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Review (50-74)</span>
                <span className="font-semibold text-yellow-600">{stats.tierBreakdown.review}</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-yellow-500"
                  style={{
                    width: `${(stats.tierBreakdown.review / stats.totalBids) * 100}%`
                  }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Low (&lt;50)</span>
                <span className="font-semibold text-red-600">{stats.tierBreakdown.low}</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-red-500"
                  style={{
                    width: `${(stats.tierBreakdown.low / stats.totalBids) * 100}%`
                  }}
                />
              </div>
            </div>
          </div>
        </Card>

        {/* Decision Breakdown */}
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Decision Breakdown</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Pursued</span>
                <span className="font-semibold text-blue-600">{stats.decisionRate.pursue}</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500"
                  style={{
                    width: `${(stats.decisionRate.pursue / stats.totalBids) * 100}%`
                  }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Passed</span>
                <span className="font-semibold text-gray-600">{stats.decisionRate.pass}</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gray-500"
                  style={{
                    width: `${(stats.decisionRate.pass / stats.totalBids) * 100}%`
                  }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Pending</span>
                <span className="font-semibold text-orange-600">{stats.decisionRate.pending}</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-orange-500"
                  style={{
                    width: `${(stats.decisionRate.pending / stats.totalBids) * 100}%`
                  }}
                />
              </div>
            </div>
          </div>
        </Card>

        {/* Top Categories */}
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Top Categories</h3>
          <div className="space-y-2">
            {topCategories.map(([category, count]) => (
              <div key={category} className="flex justify-between items-center">
                <span className="text-sm">{category}</span>
                <span className="font-semibold">{count}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Top Locations */}
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Top Locations</h3>
          <div className="space-y-2">
            {topLocations.map(([location, count]) => (
              <div key={location} className="flex justify-between items-center">
                <span className="text-sm">{location}</span>
                <span className="font-semibold">{count}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
