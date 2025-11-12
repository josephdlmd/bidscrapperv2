'use client'

import { useEffect, useState } from 'react'
import { Download, Search } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BidTable } from '@/components/features/BidTable'
import { initializeSampleData } from '@/lib/data/sampleData'
import { getBids, getScores, getDecisions, getCurrentCompany, saveScore } from '@/lib/storage/localStorage'
import { BidScorer } from '@/lib/scoring/BidScorer'
import { exportToCSV } from '@/lib/utils'
import type { ScoredBid } from '@/types'

export default function OpportunitiesPage() {
  const [scoredBids, setScoredBids] = useState<ScoredBid[]>([])
  const [filteredBids, setFilteredBids] = useState<ScoredBid[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [locationFilter, setLocationFilter] = useState('all')
  const [tierFilter, setTierFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    initializeSampleData()
    loadBids()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [scoredBids, searchQuery, categoryFilter, locationFilter, tierFilter])

  const loadBids = () => {
    const bids = getBids()
    const company = getCurrentCompany()
    const scores = getScores()
    const decisions = getDecisions()

    if (company) {
      const scorer = new BidScorer()

      const scored: ScoredBid[] = bids.map(bid => {
        let score = scores.find(s => s.bidId === bid.id && s.companyId === company.id)

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

          saveScore(score)
        }

        const decision = decisions.find(d => d.bidId === bid.id && d.companyId === company.id)

        return { ...bid, score, decision }
      })

      setScoredBids(scored)
    }

    setLoading(false)
  }

  const applyFilters = () => {
    let filtered = [...scoredBids]

    // Search
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(bid =>
        bid.title.toLowerCase().includes(query) ||
        bid.procuringEntity.toLowerCase().includes(query) ||
        bid.category.toLowerCase().includes(query)
      )
    }

    // Category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(bid => bid.category === categoryFilter)
    }

    // Location filter
    if (locationFilter !== 'all') {
      filtered = filtered.filter(bid => bid.areaOfDelivery === locationFilter)
    }

    // Tier filter
    if (tierFilter !== 'all') {
      filtered = filtered.filter(bid => bid.score?.tier === tierFilter)
    }

    // Sort by score descending
    filtered.sort((a, b) => (b.score?.totalScore || 0) - (a.score?.totalScore || 0))

    setFilteredBids(filtered)
  }

  const handleExport = () => {
    const priorityBids = filteredBids.filter(b => b.score?.tier === 'priority')
    const filename = `pursuit_list_${new Date().toISOString().split('T')[0]}.csv`
    exportToCSV(priorityBids, filename)
  }

  const uniqueCategories = [...new Set(scoredBids.map(b => b.category))].sort()
  const uniqueLocations = [...new Set(scoredBids.map(b => b.areaOfDelivery))].sort()

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bid Opportunities</h1>
          <p className="text-gray-600">Browse and evaluate all available opportunities</p>
        </div>
        <Button onClick={handleExport} disabled={filteredBids.length === 0}>
          <Download className="mr-2 h-4 w-4" />
          Export CSV
        </Button>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search bids..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Category Filter */}
          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger>
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {uniqueCategories.map(cat => (
                <SelectItem key={cat} value={cat}>{cat}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Location Filter */}
          <Select value={locationFilter} onValueChange={setLocationFilter}>
            <SelectTrigger>
              <SelectValue placeholder="All Locations" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Locations</SelectItem>
              {uniqueLocations.map(loc => (
                <SelectItem key={loc} value={loc}>{loc}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Tier Filter */}
          <Select value={tierFilter} onValueChange={setTierFilter}>
            <SelectTrigger>
              <SelectValue placeholder="All Tiers" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Tiers</SelectItem>
              <SelectItem value="priority">Priority</SelectItem>
              <SelectItem value="review">Review</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="mt-3 text-sm text-gray-600">
          Showing {filteredBids.length} of {scoredBids.length} opportunities
        </div>
      </Card>

      {/* Bids Table */}
      <BidTable bids={filteredBids} onUpdate={loadBids} />
    </div>
  )
}
