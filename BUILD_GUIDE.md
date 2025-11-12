# Bid Intelligence - Frontend Build Guide (localStorage Version)

## Quick Setup

### 1. Create the Next.js app:

```bash
npx create-next-app@latest bid-intelligence --typescript --tailwind --app --src-dir --no-git
cd bid-intelligence
```

When prompted, choose:
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ src/ directory
- ✅ App Router
- ❌ No custom import alias (use default @/*)

### 2. Install dependencies:

```bash
npm install zustand date-fns lucide-react
npm install -D @types/node
```

### 3. Install shadcn/ui:

```bash
npx shadcn-ui@latest init
```

When prompted:
- Style: **Default**
- Base color: **Slate**
- CSS variables: **Yes**

```bash
npx shadcn-ui@latest add button card table select input badge dialog dropdown-menu
```

### 4. Copy all the files from the BUILD_FILES/ directory into your project

### 5. Run the development server:

```bash
npm run dev
```

Visit http://localhost:3000

---

## Project Structure

```
bid-intelligence/
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                 # Landing/Dashboard
│   │   ├── opportunities/
│   │   │   └── page.tsx
│   │   ├── companies/
│   │   │   └── page.tsx
│   │   ├── analytics/
│   │   │   └── page.tsx
│   │   └── history/
│   │       └── page.tsx
│   ├── components/
│   │   ├── ui/                      # shadcn components
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   └── features/
│   │       ├── BidTable.tsx
│   │       ├── BidFilters.tsx
│   │       ├── CompanyForm.tsx
│   │       └── ScoreBreakdown.tsx
│   ├── lib/
│   │   ├── scoring/
│   │   │   └── BidScorer.ts
│   │   ├── storage/
│   │   │   └── localStorage.ts
│   │   ├── data/
│   │   │   └── sampleData.ts
│   │   └── utils.ts
│   └── types/
│       └── index.ts
└── package.json
```

---

## Features Implemented

### ✅ Data Storage (localStorage)
- Companies and profiles
- Bid opportunities
- Pursuit decisions
- Calculated scores
- Auto-save on every change

### ✅ Core Pages
1. **Dashboard** - KPIs, recent priority bids, charts
2. **Opportunities** - Full bid list with filters, search, scoring
3. **Companies** - Create/edit company profiles
4. **Analytics** - Pursuit success rate, category breakdown
5. **History** - All pursue/pass decisions

### ✅ Key Features
- Real-time bid scoring
- Advanced filtering (category, location, agency, tier)
- Search functionality
- Pursue/Pass decision tracking
- CSV export
- Score breakdown modal
- Responsive design

### ✅ Sample Data
- 20 sample bids (Philippine government opportunities)
- 1 default company profile
- Pre-calculated scores

---

## How to Use

### First Time Setup

1. App loads with sample data automatically
2. View Dashboard to see overview
3. Go to Opportunities to see scored bids
4. Click "View Score" to see breakdown
5. Click "Pursue" or "Pass" to make decisions

### Create Your Company Profile

1. Go to Companies page
2. Fill in your details:
   - Expertise areas
   - Warehouse location
   - Geographic reach
   - Budget range
   - Preferred agencies
   - Preferred procurement modes
3. Click Save
4. All bids will be re-scored automatically

### Working with Bids

1. **Opportunities page** shows all bids with scores
2. **Filter** by category, location, agency, or tier
3. **Search** by title, agency, or category
4. **Sort** by score, closing date, or budget
5. **View Score** to see factor breakdown
6. **Pursue/Pass** to track decisions
7. **Export CSV** to download qualified bids

---

## localStorage Data Structure

All data is stored in browser localStorage:

```javascript
localStorage.getItem('bid-intelligence-companies')
localStorage.getItem('bid-intelligence-bids')
localStorage.getItem('bid-intelligence-decisions')
localStorage.getItem('bid-intelligence-scores')
```

### Reset Data

Open browser console and run:
```javascript
localStorage.clear()
location.reload()
```

---

## Next Steps

### Phase 1: Test & Iterate (Now)
- ✅ Play with the app
- ✅ Test scoring with different profiles
- ✅ Identify missing features
- ✅ Refine UX

### Phase 2: Enhancements
- Add more sample bids
- Customize scoring weights
- Add more filters
- Improve analytics

### Phase 3: Add Backend (Later)
- Swap localStorage → Supabase
- Add authentication
- Multi-user support
- Real-time bid updates

---

## Troubleshooting

### "Module not found" errors
```bash
npm install
```

### Styles not loading
```bash
npm run dev
# Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
```

### Data not persisting
- Check browser console for errors
- Make sure localStorage is enabled
- Try incognito mode

---

## File Creation Checklist

Copy these files from BUILD_FILES/:

Core:
- [ ] src/lib/scoring/BidScorer.ts
- [ ] src/lib/storage/localStorage.ts
- [ ] src/lib/data/sampleData.ts
- [ ] src/types/index.ts

Pages:
- [ ] src/app/page.tsx
- [ ] src/app/layout.tsx
- [ ] src/app/opportunities/page.tsx
- [ ] src/app/companies/page.tsx
- [ ] src/app/analytics/page.tsx
- [ ] src/app/history/page.tsx

Components:
- [ ] src/components/layout/Header.tsx
- [ ] src/components/layout/Sidebar.tsx
- [ ] src/components/features/BidTable.tsx
- [ ] src/components/features/BidFilters.tsx
- [ ] src/components/features/CompanyForm.tsx
- [ ] src/components/features/ScoreBreakdown.tsx

Ready to build! 🚀
