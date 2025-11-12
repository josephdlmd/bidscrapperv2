'use client'

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Card } from '@/components/ui/card'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { ScoredBid, BidScore } from '@/types'

interface ScoreBreakdownProps {
  bid: ScoredBid
  score: BidScore
  open: boolean
  onClose: () => void
}

const factorLabels = {
  categoryMatch: 'Category Match',
  geographicFeasibility: 'Geographic Feasibility',
  budgetAlignment: 'Budget Alignment',
  agencyRelationship: 'Agency Relationship',
  procurementFit: 'Procurement Fit',
  timeline: 'Timeline'
}

const factorWeights = {
  categoryMatch: 30,
  geographicFeasibility: 25,
  budgetAlignment: 20,
  agencyRelationship: 10,
  procurementFit: 10,
  timeline: 5
}

export function ScoreBreakdown({ bid, score, open, onClose }: ScoreBreakdownProps) {
  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getBarColor = (score: number) => {
    if (score >= 75) return 'bg-green-500'
    if (score >= 50) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Score Breakdown</DialogTitle>
        </DialogHeader>

        {/* Bid Summary */}
        <div className="space-y-2 pb-4 border-b">
          <h3 className="font-semibold text-lg">{bid.title}</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-gray-500">Agency:</span> {bid.procuringEntity}
            </div>
            <div>
              <span className="text-gray-500">Budget:</span> {formatCurrency(bid.budget)}
            </div>
            <div>
              <span className="text-gray-500">Location:</span> {bid.areaOfDelivery}
            </div>
            <div>
              <span className="text-gray-500">Closing:</span> {formatDate(bid.closingDate)}
            </div>
          </div>
        </div>

        {/* Total Score */}
        <div className="text-center py-4">
          <div className={`text-5xl font-bold ${getScoreColor(score.totalScore)}`}>
            {score.totalScore}
          </div>
          <div className="text-sm text-gray-500 mt-1">Total Score (out of 100)</div>
          <div className="text-xs text-gray-400 mt-1">
            Classification: <span className="font-semibold">{score.tier.toUpperCase()}</span>
          </div>
        </div>

        {/* Recommendation */}
        {score.recommendation && (
          <Card className="p-3 bg-blue-50 border-blue-200">
            <div className="text-sm font-medium text-blue-900 mb-1">Recommendation</div>
            <div className="text-sm text-blue-800">{score.recommendation}</div>
          </Card>
        )}

        {/* Concerns */}
        {score.concerns.length > 0 && (
          <Card className="p-3 bg-yellow-50 border-yellow-200">
            <div className="text-sm font-medium text-yellow-900 mb-2">Concerns</div>
            <ul className="space-y-1">
              {score.concerns.map((concern, idx) => (
                <li key={idx} className="text-sm text-yellow-800 flex items-start gap-2">
                  <span>•</span>
                  <span>{concern}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* Factor Breakdown */}
        <div className="space-y-3">
          <h4 className="font-semibold">Score Factors</h4>
          {Object.entries(factorLabels).map(([key, label]) => {
            const factorScore = score.matchFactors[key as keyof typeof score.matchFactors]
            const weight = factorWeights[key as keyof typeof factorWeights]
            const contribution = (factorScore * weight) / 100

            return (
              <div key={key} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{label}</span>
                  <div className="flex items-center gap-2">
                    <span className={`font-semibold ${getScoreColor(factorScore)}`}>
                      {factorScore.toFixed(0)}
                    </span>
                    <span className="text-gray-400">×</span>
                    <span className="text-gray-500">{weight}%</span>
                    <span className="text-gray-400">=</span>
                    <span className="font-medium w-8 text-right">{contribution.toFixed(1)}</span>
                  </div>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getBarColor(factorScore)} transition-all`}
                    style={{ width: `${factorScore}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Calculation Summary */}
        <Card className="p-3 bg-gray-50">
          <div className="text-xs text-gray-600">
            <div className="font-semibold mb-2">Score Calculation:</div>
            <div className="space-y-1 font-mono">
              {Object.entries(factorLabels).map(([key, label]) => {
                const factorScore = score.matchFactors[key as keyof typeof score.matchFactors]
                const weight = factorWeights[key as keyof typeof factorWeights]
                const contribution = (factorScore * weight) / 100

                return (
                  <div key={key} className="flex justify-between">
                    <span>{label.substring(0, 20)}:</span>
                    <span>{factorScore.toFixed(0)} × {weight}% = {contribution.toFixed(1)}</span>
                  </div>
                )
              })}
              <div className="border-t pt-1 mt-1 flex justify-between font-semibold">
                <span>Total:</span>
                <span>{score.totalScore}</span>
              </div>
            </div>
          </div>
        </Card>
      </DialogContent>
    </Dialog>
  )
}
