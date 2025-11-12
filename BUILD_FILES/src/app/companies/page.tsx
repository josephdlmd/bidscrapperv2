'use client'

import { useEffect, useState } from 'react'
import { Building2, Save } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { getCurrentCompany, saveCompany } from '@/lib/storage/localStorage'
import { generateId } from '@/lib/utils'
import type { CompanyProfile } from '@/types'

export default function CompaniesPage() {
  const [company, setCompany] = useState<CompanyProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const existingCompany = getCurrentCompany()
    if (existingCompany) {
      setCompany(existingCompany)
    }
    setLoading(false)
  }, [])

  const handleSave = () => {
    if (!company) return

    const updatedCompany = {
      ...company,
      updatedAt: new Date()
    }

    saveCompany(updatedCompany)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)

    // Reload page to re-score all bids
    window.location.reload()
  }

  const updateField = (field: keyof CompanyProfile, value: any) => {
    setCompany(prev => prev ? { ...prev, [field]: value } : null)
  }

  const updateArrayField = (field: keyof CompanyProfile, value: string) => {
    const items = value.split(',').map(s => s.trim()).filter(Boolean)
    updateField(field, items)
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>
  }

  if (!company) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Company Profile</h1>
        <Card className="p-8 text-center">
          <Building2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">No company profile found</p>
          <Button onClick={() => setCompany({
            id: generateId('company'),
            name: '',
            expertise: [],
            warehouseLocation: '',
            geographicReach: [],
            budgetRange: { min: 0, max: 0 },
            preferredAgencies: [],
            preferredProcurement: [],
            createdAt: new Date(),
            updatedAt: new Date()
          })}>
            Create Company Profile
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Company Profile</h1>
          <p className="text-gray-600">Configure your company capabilities and preferences</p>
        </div>
        <Button onClick={handleSave} className="gap-2">
          <Save className="h-4 w-4" />
          {saved ? 'Saved!' : 'Save Changes'}
        </Button>
      </div>

      <Card className="p-6 space-y-6">
        {/* Company Name */}
        <div>
          <label className="block text-sm font-medium mb-2">Company Name</label>
          <Input
            value={company.name}
            onChange={(e) => updateField('name', e.target.value)}
            placeholder="e.g., ABC Medical Supplies Corp"
          />
        </div>

        {/* Expertise */}
        <div>
          <label className="block text-sm font-medium mb-2">Expertise / Categories</label>
          <Input
            value={company.expertise.join(', ')}
            onChange={(e) => updateArrayField('expertise', e.target.value)}
            placeholder="e.g., medical supplies, healthcare, ppe, emergency equipment"
          />
          <p className="text-xs text-gray-500 mt-1">Separate multiple items with commas</p>
        </div>

        {/* Warehouse Location */}
        <div>
          <label className="block text-sm font-medium mb-2">Warehouse Location</label>
          <Input
            value={company.warehouseLocation}
            onChange={(e) => updateField('warehouseLocation', e.target.value)}
            placeholder="e.g., Makati City, Quezon City, Caloocan City"
          />
          <p className="text-xs text-gray-500 mt-1">
            Available: Caloocan City, Makati City, Valenzuela City, Quezon City
          </p>
        </div>

        {/* Geographic Reach */}
        <div>
          <label className="block text-sm font-medium mb-2">Geographic Reach</label>
          <Input
            value={company.geographicReach.join(', ')}
            onChange={(e) => updateArrayField('geographicReach', e.target.value)}
            placeholder="e.g., Metro Manila, Cavite, Rizal, Bulacan"
          />
          <p className="text-xs text-gray-500 mt-1">
            Available: Metro Manila, Cavite, Bulacan, Rizal, Batangas, Pampanga, Camarines Sur, Bataan
          </p>
        </div>

        {/* Budget Range */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Minimum Budget (₱)</label>
            <Input
              type="number"
              value={company.budgetRange.min}
              onChange={(e) => updateField('budgetRange', {
                ...company.budgetRange,
                min: parseInt(e.target.value) || 0
              })}
              placeholder="100000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Maximum Budget (₱)</label>
            <Input
              type="number"
              value={company.budgetRange.max}
              onChange={(e) => updateField('budgetRange', {
                ...company.budgetRange,
                max: parseInt(e.target.value) || 0
              })}
              placeholder="5000000"
            />
          </div>
        </div>

        {/* Preferred Agencies */}
        <div>
          <label className="block text-sm font-medium mb-2">Preferred Agencies</label>
          <Input
            value={company.preferredAgencies.join(', ')}
            onChange={(e) => updateArrayField('preferredAgencies', e.target.value)}
            placeholder="e.g., Department of Health, Department of Education, AFP"
          />
          <p className="text-xs text-gray-500 mt-1">Agencies you have good relationships with</p>
        </div>

        {/* Preferred Procurement Modes */}
        <div>
          <label className="block text-sm font-medium mb-2">Preferred Procurement Modes</label>
          <Input
            value={company.preferredProcurement.join(', ')}
            onChange={(e) => updateArrayField('preferredProcurement', e.target.value)}
            placeholder="e.g., public bidding, competitive bidding, shopping"
          />
          <p className="text-xs text-gray-500 mt-1">Common options: public bidding, competitive bidding, shopping, small value procurement</p>
        </div>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave} size="lg" className="gap-2">
          <Save className="h-5 w-5" />
          {saved ? 'Changes Saved!' : 'Save Company Profile'}
        </Button>
      </div>
    </div>
  )
}
