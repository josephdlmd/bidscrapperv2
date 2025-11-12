'use client'

import { Target } from 'lucide-react'

export function Header() {
  return (
    <header className="sticky top-0 z-50 h-16 border-b bg-white">
      <div className="flex h-full items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <Target className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-bold">Bid Intelligence</h1>
        </div>
        <div className="text-sm text-gray-600">
          Smart Bid Opportunity Scoring
        </div>
      </div>
    </header>
  )
}
