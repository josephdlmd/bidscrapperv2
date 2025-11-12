/**
 * localStorage utilities for client-side data persistence
 * All data is stored in browser localStorage
 */

import type { CompanyProfile, BidOpportunity, BidScore, PursuitDecision } from '@/types'

const STORAGE_KEYS = {
  COMPANIES: 'bid-intelligence-companies',
  BIDS: 'bid-intelligence-bids',
  SCORES: 'bid-intelligence-scores',
  DECISIONS: 'bid-intelligence-decisions',
} as const

// Helper to safely parse JSON from localStorage
function safeJsonParse<T>(key: string, fallback: T): T {
  if (typeof window === 'undefined') return fallback

  try {
    const item = localStorage.getItem(key)
    if (!item) return fallback
    return JSON.parse(item)
  } catch (error) {
    console.error(`Error parsing ${key}:`, error)
    return fallback
  }
}

// Helper to safely save JSON to localStorage
function safeJsonSave(key: string, data: any): void {
  if (typeof window === 'undefined') return

  try {
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.error(`Error saving ${key}:`, error)
  }
}

// ============================================================================
// COMPANIES
// ============================================================================

export function getCompanies(): CompanyProfile[] {
  const companies = safeJsonParse<CompanyProfile[]>(STORAGE_KEYS.COMPANIES, [])
  // Convert date strings back to Date objects
  return companies.map(c => ({
    ...c,
    createdAt: new Date(c.createdAt),
    updatedAt: new Date(c.updatedAt)
  }))
}

export function getCompany(id: string): CompanyProfile | undefined {
  return getCompanies().find(c => c.id === id)
}

export function saveCompany(company: CompanyProfile): void {
  const companies = getCompanies()
  const index = companies.findIndex(c => c.id === company.id)

  if (index >= 0) {
    companies[index] = { ...company, updatedAt: new Date() }
  } else {
    companies.push(company)
  }

  safeJsonSave(STORAGE_KEYS.COMPANIES, companies)
}

export function deleteCompany(id: string): void {
  const companies = getCompanies().filter(c => c.id !== id)
  safeJsonSave(STORAGE_KEYS.COMPANIES, companies)
}

export function getCurrentCompany(): CompanyProfile | undefined {
  const companies = getCompanies()
  return companies[0] // For now, return first company
}

// ============================================================================
// BIDS
// ============================================================================

export function getBids(): BidOpportunity[] {
  const bids = safeJsonParse<BidOpportunity[]>(STORAGE_KEYS.BIDS, [])
  return bids.map(b => ({
    ...b,
    closingDate: new Date(b.closingDate),
    createdAt: new Date(b.createdAt)
  }))
}

export function getBid(id: string): BidOpportunity | undefined {
  return getBids().find(b => b.id === id)
}

export function saveBid(bid: BidOpportunity): void {
  const bids = getBids()
  const index = bids.findIndex(b => b.id === bid.id)

  if (index >= 0) {
    bids[index] = bid
  } else {
    bids.push(bid)
  }

  safeJsonSave(STORAGE_KEYS.BIDS, bids)
}

export function saveBids(bids: BidOpportunity[]): void {
  safeJsonSave(STORAGE_KEYS.BIDS, bids)
}

export function deleteBid(id: string): void {
  const bids = getBids().filter(b => b.id !== id)
  safeJsonSave(STORAGE_KEYS.BIDS, bids)
}

// ============================================================================
// SCORES
// ============================================================================

export function getScores(): BidScore[] {
  const scores = safeJsonParse<BidScore[]>(STORAGE_KEYS.SCORES, [])
  return scores.map(s => ({
    ...s,
    calculatedAt: new Date(s.calculatedAt)
  }))
}

export function getScore(bidId: string, companyId: string): BidScore | undefined {
  return getScores().find(s => s.bidId === bidId && s.companyId === companyId)
}

export function saveScore(score: BidScore): void {
  const scores = getScores()
  const index = scores.findIndex(s => s.bidId === score.bidId && s.companyId === score.companyId)

  if (index >= 0) {
    scores[index] = score
  } else {
    scores.push(score)
  }

  safeJsonSave(STORAGE_KEYS.SCORES, scores)
}

export function saveScores(scores: BidScore[]): void {
  safeJsonSave(STORAGE_KEYS.SCORES, scores)
}

export function deleteScore(bidId: string, companyId: string): void {
  const scores = getScores().filter(s => !(s.bidId === bidId && s.companyId === companyId))
  safeJsonSave(STORAGE_KEYS.SCORES, scores)
}

// ============================================================================
// DECISIONS
// ============================================================================

export function getDecisions(): PursuitDecision[] {
  const decisions = safeJsonParse<PursuitDecision[]>(STORAGE_KEYS.DECISIONS, [])
  return decisions.map(d => ({
    ...d,
    createdAt: new Date(d.createdAt)
  }))
}

export function getDecision(bidId: string, companyId: string): PursuitDecision | undefined {
  return getDecisions().find(d => d.bidId === bidId && d.companyId === companyId)
}

export function saveDecision(decision: PursuitDecision): void {
  const decisions = getDecisions()
  const index = decisions.findIndex(d => d.bidId === decision.bidId && d.companyId === decision.companyId)

  if (index >= 0) {
    decisions[index] = decision
  } else {
    decisions.push(decision)
  }

  safeJsonSave(STORAGE_KEYS.DECISIONS, decisions)
}

export function deleteDecision(bidId: string, companyId: string): void {
  const decisions = getDecisions().filter(d => !(d.bidId === bidId && d.companyId === companyId))
  safeJsonSave(STORAGE_KEYS.DECISIONS, decisions)
}

// ============================================================================
// UTILITIES
// ============================================================================

export function clearAllData(): void {
  if (typeof window === 'undefined') return

  Object.values(STORAGE_KEYS).forEach(key => {
    localStorage.removeItem(key)
  })
}

export function exportData() {
  return {
    companies: getCompanies(),
    bids: getBids(),
    scores: getScores(),
    decisions: getDecisions(),
    exportedAt: new Date()
  }
}

export function importData(data: {
  companies?: CompanyProfile[]
  bids?: BidOpportunity[]
  scores?: BidScore[]
  decisions?: PursuitDecision[]
}) {
  if (data.companies) safeJsonSave(STORAGE_KEYS.COMPANIES, data.companies)
  if (data.bids) safeJsonSave(STORAGE_KEYS.BIDS, data.bids)
  if (data.scores) safeJsonSave(STORAGE_KEYS.SCORES, data.scores)
  if (data.decisions) safeJsonSave(STORAGE_KEYS.DECISIONS, data.decisions)
}
