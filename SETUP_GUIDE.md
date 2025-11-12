# Setup Guide - Bid Intelligence Application

## Prerequisites

### Required Software
- **Node.js**: v18.17 or higher ([Download](https://nodejs.org))
- **npm/pnpm/yarn**: Package manager
- **Git**: Version control
- **VS Code** (recommended): Code editor with extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - Prisma (if using Option 2)

### Optional
- **Docker**: For local PostgreSQL
- **Postman**: API testing

---

## 🟢 OPTION 1: Quick Start with Supabase

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create account → New Project
3. Save credentials:
   - Project URL
   - Anon Public Key
   - Service Role Key (keep secret!)

### Step 2: Set Up Database Schema

1. In Supabase Dashboard → SQL Editor
2. Copy and run this schema:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (handled by Supabase Auth mostly)
-- We'll add custom fields via profiles

-- Companies table
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  is_active BOOLEAN DEFAULT true
);

-- Company profiles
CREATE TABLE company_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
  expertise TEXT[] NOT NULL DEFAULT '{}',
  warehouse_location VARCHAR(255) NOT NULL,
  geographic_reach TEXT[] NOT NULL DEFAULT '{}',
  budget_min NUMERIC(15, 2) NOT NULL,
  budget_max NUMERIC(15, 2) NOT NULL,
  preferred_agencies TEXT[] NOT NULL DEFAULT '{}',
  preferred_procurement TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT valid_budget_range CHECK (budget_max >= budget_min)
);

-- Bid opportunities
CREATE TABLE bid_opportunities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  category VARCHAR(255) NOT NULL,
  budget NUMERIC(15, 2) NOT NULL,
  procuring_entity VARCHAR(500) NOT NULL,
  procurement_mode VARCHAR(255) NOT NULL,
  area_of_delivery VARCHAR(255) NOT NULL,
  closing_date TIMESTAMPTZ NOT NULL,
  delivery_days INTEGER NOT NULL,
  source_url TEXT,
  status VARCHAR(50) DEFAULT 'open',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT valid_delivery_days CHECK (delivery_days > 0)
);

-- Bid scores
CREATE TABLE bid_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  bid_id UUID REFERENCES bid_opportunities(id) ON DELETE CASCADE,
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  total_score NUMERIC(5, 2) NOT NULL,
  tier VARCHAR(50) NOT NULL,
  category_match NUMERIC(5, 2) NOT NULL,
  geo_feasibility NUMERIC(5, 2) NOT NULL,
  budget_alignment NUMERIC(5, 2) NOT NULL,
  agency_relationship NUMERIC(5, 2) NOT NULL,
  procurement_fit NUMERIC(5, 2) NOT NULL,
  timeline_score NUMERIC(5, 2) NOT NULL,
  recommendation TEXT,
  concerns TEXT[],
  calculated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_bid_company UNIQUE (bid_id, company_id),
  CONSTRAINT valid_score CHECK (total_score >= 0 AND total_score <= 100)
);

-- Pursuit decisions
CREATE TABLE pursuit_decisions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  bid_id UUID REFERENCES bid_opportunities(id) ON DELETE CASCADE,
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  decision VARCHAR(50) NOT NULL,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_bid_company_decision UNIQUE (bid_id, company_id)
);

-- Distance matrix
CREATE TABLE distance_matrix (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  from_location VARCHAR(255) NOT NULL,
  to_location VARCHAR(255) NOT NULL,
  distance_km NUMERIC(8, 2) NOT NULL,
  CONSTRAINT unique_route UNIQUE (from_location, to_location)
);

-- Create indexes
CREATE INDEX idx_bids_category ON bid_opportunities(category);
CREATE INDEX idx_bids_area ON bid_opportunities(area_of_delivery);
CREATE INDEX idx_bids_closing_date ON bid_opportunities(closing_date);
CREATE INDEX idx_bids_status ON bid_opportunities(status);
CREATE INDEX idx_scores_tier ON bid_scores(tier);
CREATE INDEX idx_scores_total_score ON bid_scores(total_score DESC);
CREATE INDEX idx_decisions_created_at ON pursuit_decisions(created_at DESC);
```

3. Insert distance matrix data:

```sql
INSERT INTO distance_matrix (from_location, to_location, distance_km) VALUES
  ('Caloocan City', 'Metro Manila', 10),
  ('Caloocan City', 'Cavite', 35),
  ('Caloocan City', 'Bulacan', 25),
  ('Caloocan City', 'Rizal', 30),
  ('Caloocan City', 'Batangas', 90),
  ('Caloocan City', 'Pampanga', 75),
  ('Caloocan City', 'Camarines Sur', 350),
  ('Caloocan City', 'Bataan', 120),
  ('Makati City', 'Metro Manila', 10),
  ('Makati City', 'Cavite', 25),
  ('Makati City', 'Bulacan', 35),
  ('Makati City', 'Rizal', 20),
  ('Makati City', 'Batangas', 85),
  ('Makati City', 'Pampanga', 85),
  ('Makati City', 'Camarines Sur', 360),
  ('Makati City', 'Bataan', 130),
  ('Valenzuela City', 'Metro Manila', 10),
  ('Valenzuela City', 'Cavite', 40),
  ('Valenzuela City', 'Bulacan', 20),
  ('Valenzuela City', 'Rizal', 35),
  ('Valenzuela City', 'Batangas', 95),
  ('Valenzuela City', 'Pampanga', 70),
  ('Valenzuela City', 'Camarines Sur', 345),
  ('Valenzuela City', 'Bataan', 115),
  ('Quezon City', 'Metro Manila', 10),
  ('Quezon City', 'Cavite', 30),
  ('Quezon City', 'Bulacan', 30),
  ('Quezon City', 'Rizal', 15),
  ('Quezon City', 'Batangas', 85),
  ('Quezon City', 'Pampanga', 80),
  ('Quezon City', 'Camarines Sur', 355),
  ('Quezon City', 'Bataan', 125);
```

4. Add sample data:

```sql
-- Sample company
INSERT INTO companies (id, name) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'Sample Medical Supplies Corp');

INSERT INTO company_profiles (
  company_id, expertise, warehouse_location, geographic_reach,
  budget_min, budget_max, preferred_agencies, preferred_procurement
) VALUES (
  '550e8400-e29b-41d4-a716-446655440000',
  ARRAY['medical supplies', 'healthcare', 'ppe'],
  'Makati City',
  ARRAY['Metro Manila', 'Cavite', 'Rizal', 'Bulacan'],
  100000,
  5000000,
  ARRAY['Department of Health', 'Department of Education'],
  ARRAY['public bidding', 'competitive bidding', 'shopping']
);

-- Sample bid
INSERT INTO bid_opportunities (
  title, category, budget, procuring_entity, procurement_mode,
  area_of_delivery, closing_date, delivery_days, description
) VALUES (
  'Supply of Medical Equipment',
  'medical supplies',
  500000,
  'Department of Health',
  'public bidding',
  'Cavite',
  NOW() + INTERVAL '14 days',
  30,
  'Procurement of various medical equipment for regional hospital'
);
```

### Step 3: Enable Row Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE pursuit_decisions ENABLE ROW LEVEL SECURITY;

-- Simple policies (customize based on your needs)
-- Allow authenticated users to read all bids
CREATE POLICY "Allow authenticated read bids"
  ON bid_opportunities FOR SELECT
  TO authenticated
  USING (true);

-- Allow users to read their own company data
CREATE POLICY "Users can read own company"
  ON companies FOR SELECT
  TO authenticated
  USING (
    id IN (
      SELECT company_id FROM auth.users
      WHERE auth.uid() = id
    )
  );

-- Add more policies as needed...
```

### Step 4: Create Next.js App

```bash
# Create Next.js app
npx create-next-app@latest bid-intelligence --typescript --tailwind --app --src-dir

# Navigate to project
cd bid-intelligence

# Install Supabase client
npm install @supabase/supabase-js @supabase/auth-helpers-nextjs

# Install shadcn/ui
npx shadcn-ui@latest init

# Install additional dependencies
npm install zustand date-fns zod lucide-react
npm install -D @types/node
```

### Step 5: Configure Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Step 6: Set Up Supabase Client

Create `src/lib/supabase/client.ts`:

```typescript
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import type { Database } from '@/types/database.types'

export const createClient = () => createClientComponentClient<Database>()
```

Create `src/lib/supabase/server.ts`:

```typescript
import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import type { Database } from '@/types/database.types'

export const createClient = () => {
  const cookieStore = cookies()
  return createServerComponentClient<Database>({ cookies: () => cookieStore })
}
```

### Step 7: Generate TypeScript Types

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref your-project-ref

# Generate types
supabase gen types typescript --linked > src/types/database.types.ts
```

### Step 8: Add shadcn Components

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add table
npx shadcn-ui@latest add select
npx shadcn-ui@latest add input
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
```

### Step 9: Create Scoring Engine

Copy `src/lib/scoring/BidScorer.ts` from the scoring engine example (see SCORING_ENGINE.md)

### Step 10: Run Development Server

```bash
npm run dev
```

Visit `http://localhost:3000`

---

## 🟡 OPTION 2: tRPC + Prisma Setup

### Step 1: Create T3 App (Fastest)

```bash
# Create app with tRPC, Prisma, NextAuth pre-configured
npx create-t3-app@latest bid-intelligence

# Choose options:
# ✅ TypeScript
# ✅ App Router
# ✅ Tailwind
# ✅ tRPC
# ✅ Prisma
# ✅ NextAuth
# ✅ Git
```

### Step 2: Set Up Database

#### Option A: Local PostgreSQL with Docker

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: biduser
      POSTGRES_PASSWORD: bidpass123
      POSTGRES_DB: biddb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
EOF

# Start services
docker-compose up -d
```

#### Option B: Cloud PostgreSQL

Use [Neon](https://neon.tech), [Supabase](https://supabase.com), or [Railway](https://railway.app)

### Step 3: Configure Environment

Create `.env`:

```env
# Database
DATABASE_URL="postgresql://biduser:bidpass123@localhost:5432/biddb"
DIRECT_URL="postgresql://biduser:bidpass123@localhost:5432/biddb"

# NextAuth
NEXTAUTH_SECRET="your-secret-here-generate-with-openssl-rand-base64-32"
NEXTAUTH_URL="http://localhost:3000"

# Redis (optional)
REDIS_URL="redis://localhost:6379"

# App
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### Step 4: Update Prisma Schema

Replace `prisma/schema.prisma` with the schema from `DATABASE_SCHEMA.md`

### Step 5: Run Migrations

```bash
# Generate Prisma client
npx prisma generate

# Create migration
npx prisma migrate dev --name init

# Seed database
npx prisma db seed
```

### Step 6: Create Seed Script

Create `prisma/seed.ts`:

```typescript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  // Seed distance matrix
  await prisma.distanceMatrix.createMany({
    data: [
      { fromLocation: 'Caloocan City', toLocation: 'Metro Manila', distanceKm: 10 },
      { fromLocation: 'Caloocan City', toLocation: 'Cavite', distanceKm: 35 },
      // ... add all distance data
    ]
  })

  // Seed sample company
  const company = await prisma.company.create({
    data: {
      name: 'Sample Medical Supplies Corp',
      profile: {
        create: {
          expertise: ['medical supplies', 'healthcare'],
          warehouseLocation: 'Makati City',
          geographicReach: ['Metro Manila', 'Cavite'],
          budgetMin: 100000,
          budgetMax: 5000000,
          preferredAgencies: ['Department of Health'],
          preferredProcurement: ['public bidding']
        }
      }
    }
  })

  console.log('Seeded:', company)
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
```

Add to `package.json`:

```json
{
  "prisma": {
    "seed": "tsx prisma/seed.ts"
  }
}
```

### Step 7: Create tRPC Routers

Create `src/server/api/routers/bid.router.ts`:

```typescript
import { z } from 'zod'
import { createTRPCRouter, protectedProcedure } from '../trpc'
import { BidScorer } from '@/lib/scoring/BidScorer'

export const bidRouter = createTRPCRouter({
  getAll: protectedProcedure
    .input(z.object({
      limit: z.number().min(1).max(100).default(50),
      offset: z.number().default(0)
    }))
    .query(async ({ ctx, input }) => {
      return await ctx.db.bidOpportunity.findMany({
        take: input.limit,
        skip: input.offset,
        orderBy: { closingDate: 'asc' }
      })
    }),

  scoreBid: protectedProcedure
    .input(z.object({
      bidId: z.string(),
      companyId: z.string()
    }))
    .mutation(async ({ ctx, input }) => {
      const bid = await ctx.db.bidOpportunity.findUnique({
        where: { id: input.bidId }
      })

      const company = await ctx.db.companyProfile.findUnique({
        where: { companyId: input.companyId }
      })

      if (!bid || !company) throw new Error('Not found')

      const scorer = new BidScorer()
      const result = scorer.scoreBid(bid, company)

      return await ctx.db.bidScore.create({
        data: result
      })
    })
})
```

### Step 8: Install Additional Dependencies

```bash
npm install @tanstack/react-table
npm install recharts
npm install date-fns
npm install -D tsx
```

### Step 9: Run Development

```bash
# Terminal 1: Start database
docker-compose up

# Terminal 2: Start dev server
npm run dev
```

---

## Common Next Steps (Both Options)

### 1. Set Up Authentication

#### Supabase (Option 1)
Already built-in! Use Supabase Auth UI components.

#### NextAuth (Option 2)
Configure providers in `src/server/auth.ts`

### 2. Create First Page

`src/app/dashboard/page.tsx`:

```typescript
import { createClient } from '@/lib/supabase/server'

export default async function DashboardPage() {
  const supabase = createClient()

  const { data: bids } = await supabase
    .from('bid_opportunities')
    .select('*')
    .limit(10)

  return (
    <div>
      <h1>Dashboard</h1>
      {/* Render bids */}
    </div>
  )
}
```

### 3. Add Scoring Logic

Copy the `BidScorer` class and integrate it.

### 4. Build UI Components

Start with the opportunities table, then add filters, etc.

---

## Troubleshooting

### "Module not found" errors
```bash
npm install
```

### Supabase connection issues
- Check `.env.local` has correct URLs
- Verify Supabase project is running
- Check firewall settings

### Database connection failed
```bash
# Check PostgreSQL is running
docker ps

# View logs
docker-compose logs postgres
```

### Type errors
```bash
# Regenerate Prisma client
npx prisma generate

# Or Supabase types
supabase gen types typescript --linked > src/types/database.types.ts
```

---

## Next Steps

1. ✅ Review `BID_INTELLIGENCE_ANALYSIS.md` for business logic
2. ✅ Check `DATABASE_SCHEMA.md` for data model
3. ✅ See `PROJECT_STRUCTURE.md` for organization
4. ✅ Read `SCORING_ENGINE.md` for algorithm implementation
5. 🚀 Start building features!

---

## Useful Commands

```bash
# Development
npm run dev                  # Start dev server
npm run build               # Production build
npm run start               # Start production server

# Database (Prisma)
npx prisma studio           # Visual database editor
npx prisma migrate dev      # Create migration
npx prisma db push          # Push schema (no migration)
npx prisma db seed          # Seed database

# Database (Supabase)
supabase start              # Start local Supabase
supabase db reset           # Reset database
supabase gen types typescript

# Testing
npm run test                # Run tests
npm run test:watch          # Watch mode
npm run type-check          # TypeScript check

# Code Quality
npm run lint                # ESLint
npm run format              # Prettier
```

---

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Prisma Docs](https://www.prisma.io/docs)
- [tRPC Docs](https://trpc.io/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com/docs)

Happy coding! 🎉
