'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ArrowRight, TrendingUp, TrendingDown, FileText, CheckCircle2, XCircle } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { initializeSampleData } from '@/lib/data/sampleData'
import { getBids, getScores, getDecisions, getCurrentCompany, saveScore } from '@/lib/storage/localStorage'
import { BidScorer } from '@/lib/scoring/BidScorer'
import { formatCurrency, formatRelativeTime, getTierColor, getTierLabel } from '@/lib/utils'
import type { ScoredBid } from '@/types'

export default function DashboardPage() {
  const [scoredBids, setScoredBids] = useState<ScoredBid[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Initialize sample data on first load
    initializeSampleData()

    // Load and score bids
    const bids = getBids()
    const company = getCurrentCompany()
    const scores = getScores()
    const decisions = getDecisions()

    if (company) {
      const scorer = new BidScorer()

      const scored: ScoredBid[] = bids.map(bid => {
        // Check if we have a cached score
        let score = scores.find(s => s.bidId === bid.id && s.companyId === company.id)

        // Calculate if not cached
        if (!score) {
          const result = scorer.scoreBid(
            {
              category: bid.category,
              budget: bid.budget,
              area_of_delivery: bid.areaOfDelivery,
              opportunity_procuring_entity: bid.procuringEntity,
              procurement_mode: bid.procurementMode,
              closing_date: bid.closingDate,
              delivery_days: bid.deliveryDays
            },
            {
              expertise: company.expertise,
              warehouseLocation: company.warehouseLocation,
              geographicReach: company.geographicReach,
              budgetRange: company.budgetRange,
              preferredAgencies: company.preferredAgencies,
              preferredProcurement: company.preferredProcurement
            }
          )

          score = {
            id: `score-${bid.id}-${company.id}`,
            bidId: bid.id,
            companyId: company.id,
            totalScore: result.score,
            tier: result.tier,
            matchFactors: result.matchFactors,
            recommendation: result.recommendation,
            concerns: result.concerns,
            calculatedAt: new Date()
          }

          // Cache the score
          saveScore(score)
        }

        const decision = decisions.find(d => d.bidId === bid.id && d.companyId === company.id)

        return { ...bid, score, decision }
      })

      setScoredBids(scored)
    }

    setLoading(false)
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  const priorityBids = scoredBids.filter(b => b.score?.tier === 'priority')
  const reviewBids = scoredBids.filter(b => b.score?.tier === 'review')
  const lowBids = scoredBids.filter(b => b.score?.tier === 'low')
  const pursuedBids = scoredBids.filter(b => b.decision?.decision === 'pursue')
  const passedBids = scoredBids.filter(b => b.decision?.decision === 'pass')

  const topPriority = scoredBids
    .filter(b => b.score?.tier === 'priority')
    .sort((a, b) => (b.score?.totalScore || 0) - (a.score?.totalScore || 0))
    .slice(0, 5)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-600">Overview of bid opportunities and your pursuit activity</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Opportunities</p>
              <p className="text-3xl font-bold mt-1">{scoredBids.length}</p>
            </div>
            <FileText className="h-10 w-10 text-gray-400" />
          </div>
        </Card>

        <Card className="p-6 border-green-200 bg-green-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-700">Priority Bids</p>
              <p className="text-3xl font-bold text-green-700 mt-1">{priorityBids.length}</p>
            </div>
            <TrendingUp className="h-10 w-10 text-green-600" />
          </div>
        </Card>

        <Card className="p-6 border-yellow-200 bg-yellow-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-yellow-700">Review Needed</p>
              <p className="text-3xl font-bold text-yellow-700 mt-1">{reviewBids.length}</p>
            </div>
            <TrendingDown className="h-10 w-10 text-yellow-600" />
          </div>
        </Card>

        <Card className="p-6 border-blue-200 bg-blue-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-700">Pursued</p>
              <p className="text-3xl font-bold text-blue-700 mt-1">{pursuedBids.length}</p>
            </div>
            <CheckCircle2 className="h-10 w-10 text-blue-600" />
          </div>
        </Card>

        <Card className="p-6 border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Passed</p>
              <p className="text-3xl font-bold text-gray-700 mt-1">{passedBids.length}</p>
            </div>
            <XCircle className="h-10 w-10 text-gray-400" />
          </div>
        </Card>

        <Card className="p-6 border-red-200 bg-red-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-700">Low Priority</p>
              <p className="text-3xl font-bold text-red-700 mt-1">{lowBids.length}</p>
            </div>
            <FileText className="h-10 w-10 text-red-600" />
          </div>
        </Card>
      </div>

      {/* Top Priority Opportunities */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Top Priority Opportunities</h2>
          <Link href="/opportunities">
            <Button variant="outline" size="sm">
              View All
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>

        <div className="space-y-3">
          {topPriority.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No priority opportunities found</p>
          ) : (
            topPriority.map(bid => (
              <div
                key={bid.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium">{bid.title}</h3>
                    <span className={`px-2 py-0.5 text-xs rounded border ${getTierColor(bid.score!.tier)}`}>
                      {getTierLabel(bid.score!.tier)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{bid.procuringEntity}</p>
                  <div className="flex gap-4 mt-2 text-xs text-gray-500">
                    <span>{formatCurrency(bid.budget)}</span>
                    <span>•</span>
                    <span>{bid.areaOfDelivery}</span>
                    <span>•</span>
                    <span>Closes {formatRelativeTime(bid.closingDate)}</span>
                  </div>
                </div>
                <div className="text-right ml-4">
                  <div className="text-2xl font-bold text-green-600">{bid.score?.totalScore}</div>
                  <div className="text-xs text-gray-500">Score</div>
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Score Distribution</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm">Priority (≥75)</span>
              <span className="font-semibold text-green-600">{priorityBids.length}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Review (50-74)</span>
              <span className="font-semibold text-yellow-600">{reviewBids.length}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Low (&lt;50)</span>
              <span className="font-semibold text-red-600">{lowBids.length}</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold mb-4">Decision Summary</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm">Pursued</span>
              <span className="font-semibold text-blue-600">{pursuedBids.length}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Passed</span>
              <span className="font-semibold text-gray-600">{passedBids.length}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Pending</span>
              <span className="font-semibold">{scoredBids.length - pursuedBids.length - passedBids.length}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
