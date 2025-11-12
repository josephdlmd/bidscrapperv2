/**
 * BidScorer.ts
 *
 * Main scoring engine for bid opportunities
 * Implements the 6-factor weighted scoring algorithm
 *
 * Usage:
 *   const scorer = new BidScorer()
 *   const result = scorer.scoreBid(bid, companyProfile)
 */

// ============================================================================
// TYPES
// ============================================================================

export interface BudgetRange {
  min: number
  max: number
}

export interface CompanyProfile {
  expertise: string[]
  warehouseLocation: string
  geographicReach: string[]
  budgetRange: BudgetRange
  preferredAgencies: string[]
  preferredProcurement: string[]
}

export interface BidOpportunity {
  category: string
  budget: number
  area_of_delivery: string
  opportunity_procuring_entity: string
  opportunity_project_title?: string
  procurement_mode: string
  closing_date: Date | string
  delivery_days: number
}

export interface MatchFactors {
  categoryMatch: number
  geographicFeasibility: number
  budgetAlignment: number
  agencyRelationship: number
  procurementFit: number
  timeline: number
}

export interface ScoredBid extends BidOpportunity {
  score: number
  tier: 'priority' | 'review' | 'low'
  matchFactors: MatchFactors
  recommendation: string
  concerns: string[]
}

// ============================================================================
// CONSTANTS
// ============================================================================

const SCORE_WEIGHTS = {
  categoryMatch: 0.30,
  geographicFeasibility: 0.25,
  budgetAlignment: 0.20,
  agencyRelationship: 0.10,
  procurementFit: 0.10,
  timeline: 0.05
} as const

const TIER_THRESHOLDS = {
  PRIORITY: 75,
  REVIEW: 50
} as const

const DISTANCE_SCORES = {
  EXCELLENT: { max: 20, score: 100 },
  GOOD: { max: 50, score: 85 },
  MODERATE: { max: 100, score: 70 },
  POOR: { max: 200, score: 50 },
  VERY_POOR: { score: 30 },
  OUTSIDE: { score: 10 }
} as const

// Related category mappings for partial matching
const CATEGORY_MAPPINGS: Record<string, string[]> = {
  'medical supplies': ['healthcare', 'emergency', 'first aid', 'ppe'],
  'emergency equipment': ['medical', 'safety', 'disaster', 'rescue'],
  'it equipment': ['computer', 'software', 'technology', 'office'],
  'construction materials': ['tools', 'building', 'infrastructure'],
  'food': ['catering', 'prepared', 'preserved', 'meals']
}

// Philippine distance matrix (in kilometers)
const DISTANCE_MATRIX: Record<string, Record<string, number>> = {
  'Caloocan City': {
    'Metro Manila': 10,
    'Cavite': 35,
    'Bulacan': 25,
    'Rizal': 30,
    'Batangas': 90,
    'Pampanga': 75,
    'Camarines Sur': 350,
    'Bataan': 120
  },
  'Makati City': {
    'Metro Manila': 10,
    'Cavite': 25,
    'Bulacan': 35,
    'Rizal': 20,
    'Batangas': 85,
    'Pampanga': 85,
    'Camarines Sur': 360,
    'Bataan': 130
  },
  'Valenzuela City': {
    'Metro Manila': 10,
    'Cavite': 40,
    'Bulacan': 20,
    'Rizal': 35,
    'Batangas': 95,
    'Pampanga': 70,
    'Camarines Sur': 345,
    'Bataan': 115
  },
  'Quezon City': {
    'Metro Manila': 10,
    'Cavite': 30,
    'Bulacan': 30,
    'Rizal': 15,
    'Batangas': 85,
    'Pampanga': 80,
    'Camarines Sur': 355,
    'Bataan': 125
  }
}

// ============================================================================
// MAIN CLASS
// ============================================================================

export class BidScorer {
  /**
   * Calculate distance between warehouse and delivery location
   */
  private calculateDistance(warehouse: string, delivery: string): number {
    const warehouseData = DISTANCE_MATRIX[warehouse] || DISTANCE_MATRIX['Caloocan City']
    return warehouseData[delivery] || 100 // Default 100km if not found
  }

  /**
   * Factor 1: Category Match (30% weight)
   *
   * Scoring:
   * - Exact match: 100 points
   * - Partial/substring match: 75 points
   * - Related category: 50 points
   * - No match: 0 points
   */
  calculateCategoryMatch(bidCategory: string, companyExpertise: string[]): number {
    const categoryLower = bidCategory.toLowerCase()

    // Exact match
    if (companyExpertise.some(exp => exp.toLowerCase() === categoryLower)) {
      return 100
    }

    // Partial/substring match
    const hasPartialMatch = companyExpertise.some(exp => {
      const expLower = exp.toLowerCase()
      return categoryLower.includes(expLower) || expLower.includes(categoryLower)
    })

    if (hasPartialMatch) {
      return 75
    }

    // Related category mapping
    for (const [primary, related] of Object.entries(CATEGORY_MAPPINGS)) {
      const companyHasPrimary = companyExpertise.some(exp =>
        exp.toLowerCase().includes(primary)
      )
      const bidHasRelated = related.some(keyword =>
        categoryLower.includes(keyword)
      )

      if (companyHasPrimary && bidHasRelated) {
        return 50
      }
    }

    return 0
  }

  /**
   * Factor 2: Geographic Feasibility (25% weight)
   *
   * Checks if delivery location is within company's geographic reach,
   * then scores based on distance from warehouse
   */
  calculateGeographicFeasibility(
    deliveryArea: string,
    warehouseLocation: string,
    geographicReach: string[]
  ): number {
    // Check if delivery area is in company's reach
    const inReach = geographicReach.some(area =>
      deliveryArea.includes(area) || area.includes(deliveryArea)
    )

    if (!inReach) {
      return DISTANCE_SCORES.OUTSIDE.score
    }

    // Calculate distance and score accordingly
    const distance = this.calculateDistance(warehouseLocation, deliveryArea)

    if (distance <= DISTANCE_SCORES.EXCELLENT.max) return DISTANCE_SCORES.EXCELLENT.score
    if (distance <= DISTANCE_SCORES.GOOD.max) return DISTANCE_SCORES.GOOD.score
    if (distance <= DISTANCE_SCORES.MODERATE.max) return DISTANCE_SCORES.MODERATE.score
    if (distance <= DISTANCE_SCORES.POOR.max) return DISTANCE_SCORES.POOR.score

    return DISTANCE_SCORES.VERY_POOR.score
  }

  /**
   * Factor 3: Budget Alignment (20% weight)
   *
   * Scores how well the bid budget aligns with company's budget range
   * Optimal range: 2x min to 70% of max
   */
  calculateBudgetAlignment(bidBudget: number, budgetRange: BudgetRange): number {
    // Budget below company minimum
    if (bidBudget < budgetRange.min) {
      return bidBudget >= 0.5 * budgetRange.min ? 40 : 20
    }

    // Budget above company maximum
    if (bidBudget > budgetRange.max) {
      return bidBudget <= 1.5 * budgetRange.max ? 50 : 20
    }

    // Budget within range - check if in optimal range
    const optimalMin = 2 * budgetRange.min
    const optimalMax = 0.7 * budgetRange.max

    if (bidBudget >= optimalMin && bidBudget <= optimalMax) {
      return 100 // In optimal range
    }

    return 75 // In acceptable range
  }

  /**
   * Factor 4: Agency Relationship (10% weight)
   *
   * Scores based on company's relationship/preference for the procuring agency
   */
  calculateAgencyRelationship(
    procuringEntity: string,
    preferredAgencies: string[]
  ): number {
    const entityLower = procuringEntity.toLowerCase()

    // Exact match with preferred agency
    if (preferredAgencies.some(agency => agency.toLowerCase() === entityLower)) {
      return 100
    }

    // Partial match
    const hasPartialMatch = preferredAgencies.some(agency =>
      entityLower.includes(agency.toLowerCase()) ||
      agency.toLowerCase().includes(entityLower)
    )

    if (hasPartialMatch) {
      return 75
    }

    // Government entity keywords
    const governmentKeywords = ['department', 'bureau', 'commission', 'university']
    if (governmentKeywords.some(keyword => entityLower.includes(keyword))) {
      return 50
    }

    return 30 // Default for unknown agencies
  }

  /**
   * Factor 5: Procurement Fit (10% weight)
   *
   * Scores based on company's experience with the procurement mode
   */
  calculateProcurementFit(
    procurementMode: string,
    preferredProcurement: string[]
  ): number {
    const modeLower = procurementMode.toLowerCase()

    // Exact match
    if (preferredProcurement.some(pref => pref.toLowerCase() === modeLower)) {
      return 100
    }

    // Partial match
    const hasPartialMatch = preferredProcurement.some(pref =>
      modeLower.includes(pref.toLowerCase()) ||
      pref.toLowerCase().includes(modeLower)
    )

    if (hasPartialMatch) {
      return 75
    }

    // Special scoring for common modes
    if (modeLower.includes('small value')) return 80
    if (modeLower.includes('shopping')) return 70
    if (modeLower.includes('public bidding') || modeLower.includes('competitive')) return 60

    return 40 // Default
  }

  /**
   * Factor 6: Timeline Score (5% weight)
   *
   * Scores based on urgency and feasibility of timeline
   */
  calculateTimelineScore(closingDate: Date | string, deliveryDays: number): number {
    const closing = new Date(closingDate)
    const now = new Date()
    const daysUntilClosing = (closing.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)

    // Very urgent (< 3 days)
    if (daysUntilClosing < 3) return 30

    // Urgent (3-7 days)
    if (daysUntilClosing < 7) return 60

    // Ideal window (7-21 days)
    if (daysUntilClosing >= 7 && daysUntilClosing <= 21) {
      if (deliveryDays <= 30) return 100
      if (deliveryDays <= 60) return 85
      return 70
    }

    // Too far out (> 60 days)
    if (daysUntilClosing > 60) return 50

    return 75 // Default
  }

  /**
   * Main scoring function
   *
   * Calculates all factor scores, applies weights, and returns scored bid
   */
  scoreBid(bid: BidOpportunity, profile: CompanyProfile): ScoredBid {
    // Calculate all factor scores
    const matchFactors: MatchFactors = {
      categoryMatch: this.calculateCategoryMatch(bid.category, profile.expertise),
      geographicFeasibility: this.calculateGeographicFeasibility(
        bid.area_of_delivery,
        profile.warehouseLocation,
        profile.geographicReach
      ),
      budgetAlignment: this.calculateBudgetAlignment(bid.budget, profile.budgetRange),
      agencyRelationship: this.calculateAgencyRelationship(
        bid.opportunity_procuring_entity,
        profile.preferredAgencies
      ),
      procurementFit: this.calculateProcurementFit(
        bid.procurement_mode,
        profile.preferredProcurement
      ),
      timeline: this.calculateTimelineScore(bid.closing_date, bid.delivery_days)
    }

    // Calculate weighted total score
    const totalScore = Object.entries(matchFactors).reduce((sum, [factor, score]) => {
      const weight = SCORE_WEIGHTS[factor as keyof typeof SCORE_WEIGHTS]
      return sum + (score * weight)
    }, 0)

    // Determine tier
    const tier: 'priority' | 'review' | 'low' =
      totalScore >= TIER_THRESHOLDS.PRIORITY ? 'priority' :
      totalScore >= TIER_THRESHOLDS.REVIEW ? 'review' :
      'low'

    // Generate recommendation and concerns
    let recommendation = ''
    const concerns: string[] = []

    if (tier === 'priority') {
      recommendation = `Strong match: ${Math.round(matchFactors.categoryMatch)}% category alignment, favorable logistics and budget.`
    } else if (tier === 'review') {
      recommendation = 'Moderate opportunity requiring evaluation of specific factors.'

      if (matchFactors.categoryMatch < 50) {
        concerns.push('Category outside core expertise')
      }
      if (matchFactors.geographicFeasibility < 50) {
        concerns.push('Distant delivery location')
      }
      if (matchFactors.budgetAlignment < 50) {
        concerns.push('Budget outside optimal range')
      }
    } else {
      recommendation = 'Low compatibility with current capabilities.'

      if (matchFactors.categoryMatch < 30) {
        concerns.push('Unrelated category')
      }
      if (matchFactors.geographicFeasibility < 30) {
        concerns.push('Outside service area')
      }
      if (matchFactors.budgetAlignment < 30) {
        concerns.push('Budget mismatch')
      }
    }

    // Add urgent warning if closing soon
    const closing = new Date(bid.closing_date)
    const now = new Date()
    const daysUntilClosing = (closing.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)

    if (daysUntilClosing < 7 && daysUntilClosing > 0) {
      concerns.unshift(`⚠️ Closing in ${Math.ceil(daysUntilClosing)} days`)
    }

    return {
      ...bid,
      score: Math.round(totalScore),
      tier,
      matchFactors,
      recommendation,
      concerns
    }
  }

  /**
   * Batch score multiple bids
   */
  scoreBids(bids: BidOpportunity[], profile: CompanyProfile): ScoredBid[] {
    return bids.map(bid => this.scoreBid(bid, profile))
  }

  /**
   * Score and sort bids by score (descending)
   */
  scoreAndSort(bids: BidOpportunity[], profile: CompanyProfile): ScoredBid[] {
    return this.scoreBids(bids, profile).sort((a, b) => b.score - a.score)
  }

  /**
   * Get only priority tier bids
   */
  getPriorityBids(bids: BidOpportunity[], profile: CompanyProfile): ScoredBid[] {
    return this.scoreBids(bids, profile)
      .filter(bid => bid.tier === 'priority')
      .sort((a, b) => b.score - a.score)
  }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Format score for display
 */
export function formatScore(score: number): string {
  return `${score}/100`
}

/**
 * Get tier badge color
 */
export function getTierColor(tier: 'priority' | 'review' | 'low'): string {
  switch (tier) {
    case 'priority': return 'green'
    case 'review': return 'yellow'
    case 'low': return 'red'
  }
}

/**
 * Get tier label
 */
export function getTierLabel(tier: 'priority' | 'review' | 'low'): string {
  switch (tier) {
    case 'priority': return 'Priority'
    case 'review': return 'Review'
    case 'low': return 'Low Priority'
  }
}

// ============================================================================
// EXAMPLE USAGE
// ============================================================================

/*
// Example company profile
const companyProfile: CompanyProfile = {
  expertise: ['medical supplies', 'healthcare', 'ppe'],
  warehouseLocation: 'Makati City',
  geographicReach: ['Metro Manila', 'Cavite', 'Rizal', 'Bulacan'],
  budgetRange: { min: 100000, max: 5000000 },
  preferredAgencies: ['Department of Health', 'Department of Education'],
  preferredProcurement: ['public bidding', 'competitive bidding', 'shopping']
}

// Example bid
const bid: BidOpportunity = {
  category: 'medical supplies',
  budget: 500000,
  area_of_delivery: 'Cavite',
  opportunity_procuring_entity: 'Department of Health',
  opportunity_project_title: 'Supply of Medical Equipment',
  procurement_mode: 'public bidding',
  closing_date: new Date('2024-12-31'),
  delivery_days: 30
}

// Score the bid
const scorer = new BidScorer()
const result = scorer.scoreBid(bid, companyProfile)

console.log(result)
// {
//   ...bid,
//   score: 91,
//   tier: 'priority',
//   matchFactors: {
//     categoryMatch: 100,
//     geographicFeasibility: 85,
//     budgetAlignment: 75,
//     agencyRelationship: 100,
//     procurementFit: 100,
//     timeline: 100
//   },
//   recommendation: 'Strong match: 100% category alignment, favorable logistics and budget.',
//   concerns: []
// }
*/
