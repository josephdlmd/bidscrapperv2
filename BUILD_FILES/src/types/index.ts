// Core Types for Bid Intelligence Application

export interface BudgetRange {
  min: number
  max: number
}

export interface CompanyProfile {
  id: string
  name: string
  expertise: string[]
  warehouseLocation: string
  geographicReach: string[]
  budgetRange: BudgetRange
  preferredAgencies: string[]
  preferredProcurement: string[]
  createdAt: Date
  updatedAt: Date
}

export interface BidOpportunity {
  id: string
  title: string
  description?: string
  category: string
  budget: number
  procuringEntity: string
  procurementMode: string
  areaOfDelivery: string
  closingDate: Date
  deliveryDays: number
  sourceUrl?: string
  status: 'open' | 'closed' | 'archived'
  createdAt: Date
}

export interface MatchFactors {
  categoryMatch: number
  geographicFeasibility: number
  budgetAlignment: number
  agencyRelationship: number
  procurementFit: number
  timeline: number
}

export interface BidScore {
  id: string
  bidId: string
  companyId: string
  totalScore: number
  tier: 'priority' | 'review' | 'low'
  matchFactors: MatchFactors
  recommendation: string
  concerns: string[]
  calculatedAt: Date
}

export interface PursuitDecision {
  id: string
  bidId: string
  companyId: string
  decision: 'pursue' | 'pass'
  notes?: string
  createdAt: Date
}

export interface ScoredBid extends BidOpportunity {
  score?: BidScore
  decision?: PursuitDecision
}
