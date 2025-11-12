# Project Structure Guide

## Option 1: Next.js + Supabase (Recommended MVP)

```
bid-intelligence-v2/
│
├── .env.local                          # Environment variables
├── .env.example                        # Example env file
├── .gitignore
├── next.config.js
├── tsconfig.json
├── tailwind.config.ts
├── package.json
├── README.md
│
├── public/                             # Static assets
│   ├── logo.svg
│   └── favicon.ico
│
├── supabase/                           # Supabase configuration
│   ├── migrations/                     # Database migrations
│   │   ├── 20240101_initial_schema.sql
│   │   ├── 20240102_seed_data.sql
│   │   └── 20240103_rls_policies.sql
│   ├── seed.sql                        # Initial seed data
│   └── config.toml                     # Supabase config
│
├── src/
│   │
│   ├── app/                            # Next.js 15 App Router
│   │   │
│   │   ├── (auth)/                     # Auth routes group
│   │   │   ├── layout.tsx              # Auth layout
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   │
│   │   ├── (dashboard)/                # Protected routes group
│   │   │   ├── layout.tsx              # Dashboard layout (sidebar, nav)
│   │   │   │
│   │   │   ├── page.tsx                # Dashboard home
│   │   │   │
│   │   │   ├── opportunities/
│   │   │   │   ├── page.tsx            # Opportunities list
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx        # Opportunity detail
│   │   │   │
│   │   │   ├── companies/
│   │   │   │   ├── page.tsx            # Company list
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx        # Create company
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx        # Company profile
│   │   │   │       └── edit/
│   │   │   │           └── page.tsx    # Edit profile
│   │   │   │
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx            # Analytics dashboard
│   │   │   │
│   │   │   └── history/
│   │   │       └── page.tsx            # Pursuit history
│   │   │
│   │   ├── api/                        # API routes
│   │   │   ├── bids/
│   │   │   │   ├── route.ts            # GET /api/bids
│   │   │   │   ├── [id]/
│   │   │   │   │   └── route.ts        # GET/PUT /api/bids/:id
│   │   │   │   └── score/
│   │   │   │       └── route.ts        # POST /api/bids/score
│   │   │   │
│   │   │   ├── companies/
│   │   │   │   ├── route.ts
│   │   │   │   └── [id]/
│   │   │   │       └── route.ts
│   │   │   │
│   │   │   ├── decisions/
│   │   │   │   └── route.ts
│   │   │   │
│   │   │   └── export/
│   │   │       └── csv/
│   │   │           └── route.ts        # CSV export
│   │   │
│   │   ├── layout.tsx                  # Root layout
│   │   ├── page.tsx                    # Landing page
│   │   ├── loading.tsx                 # Global loading
│   │   └── error.tsx                   # Global error
│   │
│   ├── components/                     # React components
│   │   │
│   │   ├── ui/                         # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── table.tsx
│   │   │   ├── select.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── badge.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/                     # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Navigation.tsx
│   │   │
│   │   ├── features/                   # Feature-specific components
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── KPICard.tsx
│   │   │   │   ├── RecentOpportunities.tsx
│   │   │   │   └── CategoryChart.tsx
│   │   │   │
│   │   │   ├── bids/
│   │   │   │   ├── BidTable.tsx
│   │   │   │   ├── BidRow.tsx
│   │   │   │   ├── BidFilters.tsx
│   │   │   │   ├── BidSearch.tsx
│   │   │   │   ├── ScoreBreakdown.tsx
│   │   │   │   └── PursuePassButtons.tsx
│   │   │   │
│   │   │   ├── company/
│   │   │   │   ├── CompanyForm.tsx
│   │   │   │   ├── ProfileEditor.tsx
│   │   │   │   └── CompanySelector.tsx
│   │   │   │
│   │   │   └── analytics/
│   │   │       ├── TrendChart.tsx
│   │   │       ├── PerformanceMetrics.tsx
│   │   │       └── HeatMap.tsx
│   │   │
│   │   └── shared/                     # Shared components
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorMessage.tsx
│   │       ├── EmptyState.tsx
│   │       └── Pagination.tsx
│   │
│   ├── lib/                            # Utility libraries
│   │   │
│   │   ├── supabase/
│   │   │   ├── client.ts               # Client-side Supabase
│   │   │   ├── server.ts               # Server-side Supabase
│   │   │   └── middleware.ts           # Auth middleware
│   │   │
│   │   ├── scoring/
│   │   │   ├── BidScorer.ts            # Main scoring class
│   │   │   ├── categoryMatcher.ts
│   │   │   ├── geographicScorer.ts
│   │   │   ├── budgetAligner.ts
│   │   │   └── distanceMatrix.ts       # Distance data
│   │   │
│   │   ├── validations/
│   │   │   ├── bidSchema.ts            # Zod schemas
│   │   │   ├── companySchema.ts
│   │   │   └── userSchema.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── formatters.ts           # Date, currency formatters
│   │   │   ├── exporters.ts            # CSV export logic
│   │   │   └── constants.ts            # App constants
│   │   │
│   │   └── hooks/                      # Custom React hooks
│   │       ├── useBids.ts
│   │       ├── useCompany.ts
│   │       ├── useScoring.ts
│   │       └── useAuth.ts
│   │
│   ├── types/                          # TypeScript types
│   │   ├── database.types.ts           # Generated from Supabase
│   │   ├── api.types.ts                # API request/response types
│   │   ├── scoring.types.ts            # Scoring engine types
│   │   └── index.ts                    # Exported types
│   │
│   ├── store/                          # State management (Zustand)
│   │   ├── useUserStore.ts
│   │   ├── useCompanyStore.ts
│   │   └── useFilterStore.ts
│   │
│   └── styles/
│       └── globals.css                 # Global styles
│
├── tests/                              # Test files
│   ├── unit/
│   │   ├── scoring/
│   │   │   ├── BidScorer.test.ts
│   │   │   ├── categoryMatcher.test.ts
│   │   │   └── budgetAligner.test.ts
│   │   └── utils/
│   │       └── formatters.test.ts
│   │
│   ├── integration/
│   │   └── api/
│   │       └── bids.test.ts
│   │
│   └── e2e/
│       └── dashboard.spec.ts
│
├── docs/                               # Documentation
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
│
└── scripts/                            # Utility scripts
    ├── seed-database.ts
    ├── generate-types.ts
    └── backup.sh
```

---

## Option 2: tRPC + Prisma Structure

```
bid-intelligence-v2/
│
├── prisma/
│   ├── schema.prisma                   # Database schema
│   ├── migrations/
│   │   └── 20240101_init/
│   │       └── migration.sql
│   └── seed.ts                         # Seed script
│
├── src/
│   │
│   ├── app/                            # Next.js App Router
│   │   ├── api/
│   │   │   └── trpc/
│   │   │       └── [trpc]/
│   │   │           └── route.ts        # tRPC endpoint
│   │   └── ... (similar to Option 1)
│   │
│   ├── server/                         # Backend logic
│   │   │
│   │   ├── api/
│   │   │   ├── routers/                # tRPC routers
│   │   │   │   ├── bid.router.ts
│   │   │   │   ├── company.router.ts
│   │   │   │   ├── user.router.ts
│   │   │   │   └── analytics.router.ts
│   │   │   │
│   │   │   ├── root.ts                 # Root router
│   │   │   └── trpc.ts                 # tRPC config
│   │   │
│   │   ├── auth/
│   │   │   ├── config.ts               # NextAuth config
│   │   │   └── providers.ts
│   │   │
│   │   ├── services/                   # Business logic
│   │   │   ├── bidService.ts
│   │   │   ├── scoringService.ts
│   │   │   └── companyService.ts
│   │   │
│   │   ├── db.ts                       # Prisma client
│   │   └── redis.ts                    # Redis client
│   │
│   ├── lib/
│   │   ├── trpc/
│   │   │   ├── client.ts               # tRPC client
│   │   │   └── provider.tsx            # React provider
│   │   │
│   │   └── scoring/
│   │       └── BidScorer.ts
│   │
│   └── ... (rest similar to Option 1)
│
└── ...
```

---

## Key File Examples

### `src/lib/scoring/BidScorer.ts`
```typescript
/**
 * Main scoring engine
 * Implements the 6-factor scoring algorithm
 */
export class BidScorer {
  calculateCategoryMatch(bidCategory: string, expertise: string[]): number
  calculateGeographicFeasibility(area: string, warehouse: string, reach: string[]): number
  calculateBudgetAlignment(budget: number, range: BudgetRange): number
  calculateAgencyRelationship(entity: string, preferred: string[]): number
  calculateProcurementFit(mode: string, preferred: string[]): number
  calculateTimelineScore(closing: Date, deliveryDays: number): number
  scoreBid(bid: Bid, profile: CompanyProfile): ScoredBid
}
```

### `src/app/api/bids/score/route.ts`
```typescript
/**
 * POST /api/bids/score
 * Scores a bid opportunity against company profile
 */
export async function POST(request: Request) {
  const { bidId, companyId } = await request.json()
  const scorer = new BidScorer()
  // ... scoring logic
  return Response.json(scoredBid)
}
```

### `src/components/features/bids/BidTable.tsx`
```typescript
/**
 * Main opportunities table
 * Features: sorting, filtering, pagination
 */
export function BidTable({
  bids,
  onPursue,
  onPass
}: BidTableProps) {
  // Component logic
}
```

---

## Directory Conventions

### **Components**
```
components/
├── ui/           → Reusable UI primitives (buttons, inputs)
├── layout/       → Layout components (header, sidebar)
├── features/     → Feature-specific components
└── shared/       → Shared business components
```

### **API Routes**
```
app/api/
├── [resource]/
│   ├── route.ts              → GET /api/resource (list)
│   ├── route.ts              → POST /api/resource (create)
│   └── [id]/
│       └── route.ts          → GET/PUT/DELETE /api/resource/:id
```

### **Tests**
```
tests/
├── unit/         → Pure function tests
├── integration/  → API + DB tests
└── e2e/          → Full user flow tests
```

---

## Configuration Files

### `.env.local` (Option 1 - Supabase)
```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### `.env.local` (Option 2 - Custom)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/biddb
DIRECT_URL=postgresql://user:pass@localhost:5432/biddb

# Redis
REDIS_URL=redis://localhost:6379

# NextAuth
NEXTAUTH_SECRET=xxx
NEXTAUTH_URL=http://localhost:3000

# AWS S3 (optional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET_NAME=bid-uploads
```

---

## Import Aliases (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/types/*": ["./src/types/*"],
      "@/app/*": ["./src/app/*"]
    }
  }
}
```

Usage:
```typescript
import { Button } from '@/components/ui/button'
import { BidScorer } from '@/lib/scoring/BidScorer'
import type { Bid } from '@/types'
```

---

## Naming Conventions

### **Files**
- Components: `PascalCase.tsx` (BidTable.tsx)
- Utilities: `camelCase.ts` (formatters.ts)
- Types: `camelCase.types.ts` (scoring.types.ts)
- Tests: `*.test.ts` or `*.spec.ts`

### **Components**
```typescript
// Use PascalCase
export function BidTable() {}
export const ScoreCard = () => {}
```

### **Functions**
```typescript
// Use camelCase
export function calculateScore() {}
export const formatCurrency = () => {}
```

### **Constants**
```typescript
// Use UPPER_SNAKE_CASE
export const MAX_FILE_SIZE = 5 * 1024 * 1024
export const SCORE_WEIGHTS = { ... }
```

---

## Package Scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:e2e": "playwright test",
    "type-check": "tsc --noEmit",
    "db:generate": "prisma generate",
    "db:migrate": "prisma migrate dev",
    "db:seed": "tsx prisma/seed.ts",
    "db:studio": "prisma studio"
  }
}
```

---

## Next Steps

1. Choose your tech stack (Option 1 or 2)
2. Review `SETUP_GUIDE.md` for installation steps
3. Copy the appropriate structure
4. Start building! 🚀
