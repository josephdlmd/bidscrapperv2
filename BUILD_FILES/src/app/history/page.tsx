'use client'

import { useEffect, useState } from 'react'
import { CheckCircle2, XCircle, Calendar } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { getDecisions, getBids, getScores } from '@/lib/storage/localStorage'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { PursuitDecision, BidOpportunity, BidScore } from '@/types'

interface DecisionWithDetails extends PursuitDecision {
  bid?: BidOpportunity
  score?: BidScore
}

export default function HistoryPage() {
  const [decisions, setDecisions] = useState<DecisionWithDetails[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const allDecisions = getDecisions()
    const bids = getBids()
    const scores = getScores()

    const enriched: DecisionWithDetails[] = allDecisions.map(decision => {
      const bid = bids.find(b => b.id === decision.bidId)
      const score = scores.find(s => s.bidId === decision.bidId && s.companyId === decision.companyId)

      return {
        ...decision,
        bid,
        score
      }
    })

    // Sort by date descending
    enriched.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())

    setDecisions(enriched)
    setLoading(false)
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  const pursuedCount = decisions.filter(d => d.decision === 'pursue').length
  const passedCount = decisions.filter(d => d.decision === 'pass').length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Decision History</h1>
        <p className="text-gray-600">Track all your pursuit and pass decisions</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Decisions</p>
              <p className="text-3xl font-bold mt-1">{decisions.length}</p>
            </div>
            <Calendar className="h-10 w-10 text-gray-400" />
          </div>
        </Card>

        <Card className="p-6 border-green-200 bg-green-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-700">Pursued</p>
              <p className="text-3xl font-bold text-green-700 mt-1">{pursuedCount}</p>
            </div>
            <CheckCircle2 className="h-10 w-10 text-green-600" />
          </div>
        </Card>

        <Card className="p-6 border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Passed</p>
              <p className="text-3xl font-bold text-gray-700 mt-1">{passedCount}</p>
            </div>
            <XCircle className="h-10 w-10 text-gray-400" />
          </div>
        </Card>
      </div>

      {/* Decision Timeline */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Decision Timeline</h2>

        {decisions.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No decisions made yet. Visit the Opportunities page to start evaluating bids.
          </div>
        ) : (
          <div className="space-y-4">
            {decisions.map(decision => (
              <div
                key={decision.id}
                className="flex gap-4 p-4 border rounded-lg hover:bg-gray-50 transition"
              >
                {/* Decision Icon */}
                <div className="flex-shrink-0">
                  {decision.decision === 'pursue' ? (
                    <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                      <CheckCircle2 className="h-6 w-6 text-green-600" />
                    </div>
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
                      <XCircle className="h-6 w-6 text-gray-600" />
                    </div>
                  )}
                </div>

                {/* Details */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold">{decision.bid?.title || 'Unknown Bid'}</h3>
                        <span className={`px-2 py-0.5 text-xs rounded ${
                          decision.decision === 'pursue'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {decision.decision === 'pursue' ? 'Pursued' : 'Passed'}
                        </span>
                      </div>
                      {decision.bid && (
                        <p className="text-sm text-gray-600">{decision.bid.procuringEntity}</p>
                      )}
                    </div>
                    <div className="text-right">
                      {decision.score && (
                        <div className="text-2xl font-bold text-blue-600">
                          {decision.score.totalScore}
                        </div>
                      )}
                      <div className="text-xs text-gray-500">Score</div>
                    </div>
                  </div>

                  {decision.bid && (
                    <div className="grid grid-cols-3 gap-3 text-sm mb-2">
                      <div>
                        <span className="text-gray-500">Budget:</span>{' '}
                        {formatCurrency(decision.bid.budget)}
                      </div>
                      <div>
                        <span className="text-gray-500">Location:</span>{' '}
                        {decision.bid.areaOfDelivery}
                      </div>
                      <div>
                        <span className="text-gray-500">Category:</span>{' '}
                        {decision.bid.category}
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    Decision made on {formatDate(decision.createdAt)}
                  </div>

                  {decision.notes && (
                    <div className="mt-2 text-sm text-gray-700 bg-gray-50 p-2 rounded">
                      {decision.notes}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
