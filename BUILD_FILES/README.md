# 🚀 Bid Intelligence - Frontend Application (localStorage Version)

Complete Next.js application with TypeScript, Tailwind CSS, and localStorage persistence.

## 📦 What's Included

### Core Application Files (17 files)

```
BUILD_FILES/
├── COMPLETE_BUILD.md          ← START HERE! Setup instructions
├── README.md                   ← This file
└── src/
    ├── app/                    ← Next.js 15 App Router pages
    │   ├── layout.tsx          → Root layout with Header + Sidebar
    │   ├── globals.css         → Tailwind + shadcn styles
    │   ├── page.tsx            → Dashboard (KPIs, top opportunities)
    │   ├── opportunities/
    │   │   └── page.tsx        → Main bid list with filters
    │   ├── companies/
    │   │   └── page.tsx        → Company profile editor
    │   ├── analytics/
    │   │   └── page.tsx        → Charts and statistics
    │   └── history/
    │       └── page.tsx        → Pursuit decision timeline
    │
    ├── components/
    │   ├── layout/
    │   │   ├── Header.tsx      → Top navigation bar
    │   │   └── Sidebar.tsx     → Left sidebar navigation
    │   └── features/
    │       ├── BidTable.tsx    → Bid list with pursue/pass buttons
    │       └── ScoreBreakdown.tsx → Score detail modal
    │
    ├── lib/
    │   ├── scoring/
    │   │   └── BidScorer.ts    → 6-factor scoring algorithm
    │   ├── storage/
    │   │   └── localStorage.ts → Browser storage utilities
    │   ├── data/
    │   │   └── sampleData.ts   → 20 sample bids + default company
    │   └── utils.ts            → Helper functions (currency, dates, CSV)
    │
    └── types/
        └── index.ts            → TypeScript interfaces
```

## ✨ Features Implemented

### ✅ Core Functionality
- **Real-time Scoring**: 6-factor algorithm (Category 30%, Geography 25%, Budget 20%, Agency 10%, Procurement 10%, Timeline 5%)
- **3-Tier Classification**: Priority (≥75), Review (50-74), Low (<50)
- **localStorage Persistence**: All data saved in browser
- **20 Sample Bids**: Philippine government opportunities pre-loaded

### ✅ Pages
1. **Dashboard** - KPI cards, top 5 priority bids, quick stats
2. **Opportunities** - Full bid list with search, filters (category, location, tier), sort
3. **Companies** - Profile editor (expertise, location, budget, agencies, procurement modes)
4. **Analytics** - Score distribution, decision breakdown, top categories/locations
5. **History** - Timeline of all pursue/pass decisions

### ✅ User Actions
- **View Score Breakdown**: Detailed 6-factor analysis in modal
- **Pursue/Pass**: Track decisions with timestamps
- **Export CSV**: Download priority bids
- **Filter & Search**: Real-time filtering across all fields
- **Edit Profile**: Auto-rescores all bids on save

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- npm or pnpm

### Installation (5 minutes)

```bash
# 1. Create Next.js app
npx create-next-app@latest bid-intelligence --typescript --tailwind --app --src-dir --no-git
cd bid-intelligence

# 2. Install dependencies
npm install zustand date-fns lucide-react clsx tailwind-merge

# 3. Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input select dialog badge

# 4. Copy all files
cd ..
cp -r BUILD_FILES/src/* bid-intelligence/src/

# 5. Run!
cd bid-intelligence
npm run dev
```

Visit **http://localhost:3000**

## 📊 How It Works

### Data Flow

```
1. App Loads
   ↓
2. Initialize Sample Data (if first time)
   - Default company profile
   - 20 sample bids
   ↓
3. Load from localStorage
   - Companies
   - Bids
   - Scores (cached)
   - Decisions
   ↓
4. Score All Bids
   - Use BidScorer class
   - Cache results in localStorage
   ↓
5. Display & Filter
   - Real-time filtering
   - Sort by score
   - Show tier badges
```

### Scoring Algorithm

```typescript
BidScorer.scoreBid(bid, companyProfile)
  ↓
Calculate 6 factors (0-100 each):
  1. categoryMatch         × 30% = X.X points
  2. geographicFeasibility × 25% = X.X points
  3. budgetAlignment       × 20% = X.X points
  4. agencyRelationship    × 10% = X.X points
  5. procurementFit        × 10% = X.X points
  6. timeline              ×  5% = X.X points
  ↓
Total Score (0-100) → Tier Classification
```

## 🎨 Customization

### Add More Sample Bids

Edit `src/lib/data/sampleData.ts`:

```typescript
export const sampleBids: BidOpportunity[] = [
  {
    id: 'bid-21',
    title: 'Your New Bid',
    category: 'medical supplies',
    budget: 500000,
    // ... more fields
  },
  // Add more...
]
```

### Change Scoring Weights

Edit `src/lib/scoring/BidScorer.ts`:

```typescript
const SCORE_WEIGHTS = {
  categoryMatch: 0.30,           // Change this
  geographicFeasibility: 0.25,   // Or this
  // ...
}
```

### Change Tier Thresholds

```typescript
const TIER_THRESHOLDS = {
  PRIORITY: 75,  // Change from 75 to 80?
  REVIEW: 50     // Change from 50 to 60?
}
```

## 📱 Screenshots

### Dashboard
- 6 KPI cards (Total, Priority, Review, Pursued, Passed, Low)
- Top 5 priority opportunities
- Score distribution chart
- Decision summary

### Opportunities
- Search bar
- 3 filter dropdowns (Category, Location, Tier)
- Bid cards with score badge
- Pursue/Pass buttons
- View Score modal

### Score Breakdown Modal
- Bid summary
- Total score (large number)
- Recommendation text
- Concerns list
- 6-factor breakdown with bars
- Weighted calculation shown

## 🗄️ localStorage Keys

```javascript
'bid-intelligence-companies'  // Company profiles
'bid-intelligence-bids'       // Bid opportunities
'bid-intelligence-scores'     // Calculated scores (cached)
'bid-intelligence-decisions'  // Pursue/pass decisions
```

### Clear All Data

```javascript
// In browser console:
localStorage.clear()
location.reload()
```

## 🔄 Next Steps

### Phase 1: Test & Iterate (Now)
- ✅ Run the app
- ✅ Edit company profile
- ✅ See bids re-score
- ✅ Make pursue/pass decisions
- ✅ Export CSV

### Phase 2: Enhancements
- Add more bid fields (description, contact info)
- Implement notes on decisions
- Add bid status workflow (open → pursued → won/lost)
- Create printable bid reports
- Add email notifications

### Phase 3: Backend Integration
- Replace localStorage with Supabase
- Add user authentication
- Multi-company support
- Real-time collaboration
- API for bid imports

## 📚 File Descriptions

| File | Purpose | Lines |
|------|---------|-------|
| `BidScorer.ts` | Core scoring algorithm with 6 factors | 550 |
| `localStorage.ts` | CRUD operations for browser storage | 200 |
| `sampleData.ts` | 20 sample bids + default company | 400 |
| `page.tsx` (Dashboard) | KPI cards + top opportunities | 200 |
| `opportunities/page.tsx` | Main bid list with filters | 180 |
| `BidTable.tsx` | Bid cards with actions | 150 |
| `ScoreBreakdown.tsx` | Detailed score modal | 120 |
| `companies/page.tsx` | Profile editor form | 200 |
| `history/page.tsx` | Decision timeline | 130 |
| `analytics/page.tsx` | Charts and stats | 150 |

**Total**: ~2,280 lines of production-ready code

## 🐛 Troubleshooting

### "Module not found: Can't resolve '@/components/ui/button'"

**Solution**:
```bash
npx shadcn-ui@latest add button card input select dialog badge
```

### "localStorage is not defined"

**Cause**: Server-side rendering
**Solution**: Already handled with `typeof window === 'undefined'` checks

### Bids not showing

**Check**:
1. Browser console for errors
2. localStorage has data: `localStorage.getItem('bid-intelligence-bids')`
3. Hard refresh (Cmd+Shift+R)

### Styles not loading

**Fix**:
1. Verify `globals.css` is in `src/app/`
2. Check Tailwind config
3. Restart dev server

## 📄 License

This is sample/educational code. Feel free to use and modify.

## 🤝 Contributing

This is a starting point! Suggestions:
- Add tests (Jest + React Testing Library)
- Implement error boundaries
- Add loading skeletons
- Improve mobile responsiveness
- Add dark mode

---

**Built with ❤️ using Next.js 15, TypeScript, Tailwind CSS, and shadcn/ui**

Ready to score some bids! 🎯
