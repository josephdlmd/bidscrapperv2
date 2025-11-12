'use client'

import { useState } from 'react'
import { CheckCircle2, XCircle, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ScoreBreakdown } from './ScoreBreakdown'
import { formatCurrency, formatRelativeTime, getTierColor, getTierLabel, generateId } from '@/lib/utils'
import { saveDecision, getCurrentCompany } from '@/lib/storage/localStorage'
import type { ScoredBid } from '@/types'

interface BidTableProps {
  bids: ScoredBid[]
  onUpdate: () => void
}

export function BidTable({ bids, onUpdate }: BidTableProps) {
  const [selectedBid, setSelectedBid] = useState<ScoredBid | null>(null)
  const [showScoreModal, setShowScoreModal] = useState(false)

  const handleDecision = (bid: ScoredBid, decision: 'pursue' | 'pass') => {
    const company = getCurrentCompany()
    if (!company) return

    saveDecision({
      id: generateId('decision'),
      bidId: bid.id,
      companyId: company.id,
      decision,
      createdAt: new Date()
    })

    onUpdate()
  }

  const handleViewScore = (bid: ScoredBid) => {
    setSelectedBid(bid)
    setShowScoreModal(true)
  }

  if (bids.length === 0) {
    return (
      <Card className="p-12 text-center">
        <p className="text-gray-500">No opportunities found matching your criteria</p>
      </Card>
    )
  }

  return (
    <>
      <div className="space-y-3">
        {bids.map(bid => (
          <Card key={bid.id} className="p-4 hover:shadow-md transition">
            <div className="flex gap-4">
              {/* Score Badge */}
              <div className="flex-shrink-0">
                <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex flex-col items-center justify-center text-white">
                  <div className="text-2xl font-bold">{bid.score?.totalScore}</div>
                  <div className="text-xs opacity-90">Score</div>
                </div>
              </div>

              {/* Bid Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-lg">{bid.title}</h3>
                      {bid.score && (
                        <span className={`px-2 py-0.5 text-xs rounded border ${getTierColor(bid.score.tier)}`}>
                          {getTierLabel(bid.score.tier)}
                        </span>
                      )}
                      {bid.decision && (
                        <span className={`px-2 py-0.5 text-xs rounded border ${
                          bid.decision.decision === 'pursue'
                            ? 'bg-blue-100 text-blue-800 border-blue-200'
                            : 'bg-gray-100 text-gray-800 border-gray-200'
                        }`}>
                          {bid.decision.decision === 'pursue' ? 'Pursued' : 'Passed'}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{bid.procuringEntity}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm mb-3">
                  <div>
                    <div className="text-gray-500 text-xs">Budget</div>
                    <div className="font-medium">{formatCurrency(bid.budget)}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">Location</div>
                    <div className="font-medium">{bid.areaOfDelivery}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">Category</div>
                    <div className="font-medium">{bid.category}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 text-xs">Closing</div>
                    <div className="font-medium">{formatRelativeTime(bid.closingDate)}</div>
                  </div>
                </div>

                {bid.score && bid.score.recommendation && (
                  <div className="text-sm text-gray-700 mb-2 p-2 bg-gray-50 rounded">
                    {bid.score.recommendation}
                  </div>
                )}

                {bid.score && bid.score.concerns.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {bid.score.concerns.map((concern, idx) => (
                      <span key={idx} className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                        {concern}
                      </span>
                    ))}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleViewScore(bid)}
                  >
                    <Eye className="mr-2 h-4 w-4" />
                    View Score
                  </Button>

                  {!bid.decision && (
                    <>
                      <Button
                        size="sm"
                        className="bg-green-600 hover:bg-green-700"
                        onClick={() => handleDecision(bid, 'pursue')}
                      >
                        <CheckCircle2 className="mr-2 h-4 w-4" />
                        Pursue
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDecision(bid, 'pass')}
                      >
                        <XCircle className="mr-2 h-4 w-4" />
                        Pass
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Score Breakdown Modal */}
      {selectedBid && selectedBid.score && (
        <ScoreBreakdown
          bid={selectedBid}
          score={selectedBid.score}
          open={showScoreModal}
          onClose={() => setShowScoreModal(false)}
        />
      )}
    </>
  )
}
