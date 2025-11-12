# Database Schema Design

## Overview
This document defines the complete database schema for the Bid Intelligence application rebuild.

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│     User        │◄───────┤   Company        │────────►│ CompanyProfile  │
├─────────────────┤   N:1   ├──────────────────┤   1:1   ├─────────────────┤
│ id              │         │ id               │         │ id              │
│ email           │         │ name             │         │ companyId       │
│ password_hash   │         │ createdAt        │         │ expertise[]     │
│ name            │         │ updatedAt        │         │ warehouseLocation│
│ role            │         │ isActive         │         │ geographicReach[]│
│ companyId   (FK)│         │                  │         │ budgetMin       │
│ createdAt       │         │                  │         │ budgetMax       │
│ lastLogin       │         │                  │         │ preferredAgencies[]│
└─────────────────┘         └──────────────────┘         │ preferredProcurement[]│
                                     │                    └─────────────────┘
                                     │ 1:N
                                     ▼
                            ┌──────────────────┐
                            │ BidOpportunity   │
                            ├──────────────────┤
                            │ id               │
                            │ title            │
                            │ description      │
                            │ category         │
                            │ budget           │
                            │ procuringEntity  │
                            │ procurementMode  │
                            │ areaOfDelivery   │
                            │ closingDate      │
                            │ deliveryDays     │
                            │ sourceUrl        │
                            │ status           │
                            │ createdAt        │
                            │ updatedAt        │
                            └──────────────────┘
                                     │
                                     │ 1:N
                                     ▼
                            ┌──────────────────┐
                            │ BidScore         │
                            ├──────────────────┤
                            │ id               │
                            │ bidId        (FK)│
                            │ companyId    (FK)│
                            │ totalScore       │
                            │ tier             │
                            │ categoryMatch    │
                            │ geoFeasibility   │
                            │ budgetAlignment  │
                            │ agencyRelation   │
                            │ procurementFit   │
                            │ timelineScore    │
                            │ calculatedAt     │
                            └──────────────────┘
                                     │
                                     │
                            ┌────────▼──────────┐
                            │ PursuitDecision   │
                            ├───────────────────┤
                            │ id                │
                            │ bidId         (FK)│
                            │ companyId     (FK)│
                            │ userId        (FK)│
                            │ decision          │
                            │ notes             │
                            │ createdAt         │
                            └───────────────────┘
```

---

## Table Definitions

### 1. users
Stores user accounts and authentication data.

```sql
CREATE TABLE users (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email             VARCHAR(255) UNIQUE NOT NULL,
  password_hash     VARCHAR(255) NOT NULL,
  name              VARCHAR(255) NOT NULL,
  role              VARCHAR(50) NOT NULL DEFAULT 'user', -- 'admin', 'user', 'viewer'
  company_id        UUID REFERENCES companies(id) ON DELETE SET NULL,
  created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login        TIMESTAMP WITH TIME ZONE,
  is_active         BOOLEAN DEFAULT true
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_company_id ON users(company_id);
```

### 2. companies
Organization/company information.

```sql
CREATE TABLE companies (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              VARCHAR(255) NOT NULL,
  created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_active         BOOLEAN DEFAULT true
);
```

### 3. company_profiles
Detailed company preferences and capabilities.

```sql
CREATE TABLE company_profiles (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id              UUID UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
  expertise               TEXT[] NOT NULL DEFAULT '{}',
  warehouse_location      VARCHAR(255) NOT NULL,
  geographic_reach        TEXT[] NOT NULL DEFAULT '{}',
  budget_min              NUMERIC(15, 2) NOT NULL,
  budget_max              NUMERIC(15, 2) NOT NULL,
  preferred_agencies      TEXT[] NOT NULL DEFAULT '{}',
  preferred_procurement   TEXT[] NOT NULL DEFAULT '{}',
  created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  CONSTRAINT valid_budget_range CHECK (budget_max >= budget_min)
);

CREATE INDEX idx_company_profiles_company_id ON company_profiles(company_id);
```

### 4. bid_opportunities
Government/corporate bid opportunities.

```sql
CREATE TABLE bid_opportunities (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title                 TEXT NOT NULL,
  description           TEXT,
  category              VARCHAR(255) NOT NULL,
  budget                NUMERIC(15, 2) NOT NULL,
  procuring_entity      VARCHAR(500) NOT NULL,
  procurement_mode      VARCHAR(255) NOT NULL,
  area_of_delivery      VARCHAR(255) NOT NULL,
  closing_date          TIMESTAMP WITH TIME ZONE NOT NULL,
  delivery_days         INTEGER NOT NULL,
  source_url            TEXT,
  status                VARCHAR(50) DEFAULT 'open', -- 'open', 'closed', 'archived'
  created_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  CONSTRAINT valid_delivery_days CHECK (delivery_days > 0)
);

CREATE INDEX idx_bids_category ON bid_opportunities(category);
CREATE INDEX idx_bids_area ON bid_opportunities(area_of_delivery);
CREATE INDEX idx_bids_closing_date ON bid_opportunities(closing_date);
CREATE INDEX idx_bids_status ON bid_opportunities(status);
CREATE INDEX idx_bids_procuring_entity ON bid_opportunities(procuring_entity);
```

### 5. bid_scores
Calculated scores for bid-company matches.

```sql
CREATE TABLE bid_scores (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bid_id                  UUID REFERENCES bid_opportunities(id) ON DELETE CASCADE,
  company_id              UUID REFERENCES companies(id) ON DELETE CASCADE,
  total_score             NUMERIC(5, 2) NOT NULL,
  tier                    VARCHAR(50) NOT NULL, -- 'priority', 'review', 'low'
  category_match          NUMERIC(5, 2) NOT NULL,
  geo_feasibility         NUMERIC(5, 2) NOT NULL,
  budget_alignment        NUMERIC(5, 2) NOT NULL,
  agency_relationship     NUMERIC(5, 2) NOT NULL,
  procurement_fit         NUMERIC(5, 2) NOT NULL,
  timeline_score          NUMERIC(5, 2) NOT NULL,
  recommendation          TEXT,
  concerns                TEXT[],
  calculated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  CONSTRAINT unique_bid_company UNIQUE (bid_id, company_id),
  CONSTRAINT valid_score CHECK (total_score >= 0 AND total_score <= 100)
);

CREATE INDEX idx_scores_bid_id ON bid_scores(bid_id);
CREATE INDEX idx_scores_company_id ON bid_scores(company_id);
CREATE INDEX idx_scores_tier ON bid_scores(tier);
CREATE INDEX idx_scores_total_score ON bid_scores(total_score DESC);
```

### 6. pursuit_decisions
User decisions on whether to pursue opportunities.

```sql
CREATE TABLE pursuit_decisions (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bid_id            UUID REFERENCES bid_opportunities(id) ON DELETE CASCADE,
  company_id        UUID REFERENCES companies(id) ON DELETE CASCADE,
  user_id           UUID REFERENCES users(id) ON DELETE SET NULL,
  decision          VARCHAR(50) NOT NULL, -- 'pursue', 'pass'
  notes             TEXT,
  created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  CONSTRAINT unique_bid_company_decision UNIQUE (bid_id, company_id)
);

CREATE INDEX idx_decisions_bid_id ON pursuit_decisions(bid_id);
CREATE INDEX idx_decisions_company_id ON pursuit_decisions(company_id);
CREATE INDEX idx_decisions_user_id ON pursuit_decisions(user_id);
CREATE INDEX idx_decisions_created_at ON pursuit_decisions(created_at DESC);
```

### 7. distance_matrix (Optional - for caching)
Pre-calculated distances between locations.

```sql
CREATE TABLE distance_matrix (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  from_location     VARCHAR(255) NOT NULL,
  to_location       VARCHAR(255) NOT NULL,
  distance_km       NUMERIC(8, 2) NOT NULL,

  CONSTRAINT unique_route UNIQUE (from_location, to_location)
);

CREATE INDEX idx_distance_from ON distance_matrix(from_location);
CREATE INDEX idx_distance_to ON distance_matrix(to_location);
```

---

## TypeScript Type Definitions

```typescript
// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
  companyId: string | null;
  createdAt: Date;
  updatedAt: Date;
  lastLogin: Date | null;
  isActive: boolean;
}

// Company Types
export interface Company {
  id: string;
  name: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
}

export interface CompanyProfile {
  id: string;
  companyId: string;
  expertise: string[];
  warehouseLocation: string;
  geographicReach: string[];
  budgetMin: number;
  budgetMax: number;
  preferredAgencies: string[];
  preferredProcurement: string[];
  createdAt: Date;
  updatedAt: Date;
}

// Bid Types
export interface BidOpportunity {
  id: string;
  title: string;
  description: string | null;
  category: string;
  budget: number;
  procuringEntity: string;
  procurementMode: string;
  areaOfDelivery: string;
  closingDate: Date;
  deliveryDays: number;
  sourceUrl: string | null;
  status: 'open' | 'closed' | 'archived';
  createdAt: Date;
  updatedAt: Date;
}

export interface BidScore {
  id: string;
  bidId: string;
  companyId: string;
  totalScore: number;
  tier: 'priority' | 'review' | 'low';
  categoryMatch: number;
  geoFeasibility: number;
  budgetAlignment: number;
  agencyRelationship: number;
  procurementFit: number;
  timelineScore: number;
  recommendation: string | null;
  concerns: string[];
  calculatedAt: Date;
}

export interface PursuitDecision {
  id: string;
  bidId: string;
  companyId: string;
  userId: string | null;
  decision: 'pursue' | 'pass';
  notes: string | null;
  createdAt: Date;
}

export interface DistanceMatrix {
  id: string;
  fromLocation: string;
  toLocation: string;
  distanceKm: number;
}

// Combined Types for API responses
export interface BidWithScore extends BidOpportunity {
  score?: BidScore;
  decision?: PursuitDecision;
}

export interface CompanyWithProfile extends Company {
  profile: CompanyProfile;
}
```

---

## Seed Data

### Default Distance Matrix (Philippines)
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

### Sample Company Profile
```sql
-- Insert sample company
INSERT INTO companies (id, name) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'Sample Corp');

-- Insert company profile
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
```

---

## Prisma Schema (Alternative ORM)

```prisma
// schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id              String    @id @default(uuid())
  email           String    @unique
  passwordHash    String    @map("password_hash")
  name            String
  role            String    @default("user")
  companyId       String?   @map("company_id")
  createdAt       DateTime  @default(now()) @map("created_at")
  updatedAt       DateTime  @updatedAt @map("updated_at")
  lastLogin       DateTime? @map("last_login")
  isActive        Boolean   @default(true) @map("is_active")

  company         Company?  @relation(fields: [companyId], references: [id])
  decisions       PursuitDecision[]

  @@index([email])
  @@index([companyId])
  @@map("users")
}

model Company {
  id              String    @id @default(uuid())
  name            String
  createdAt       DateTime  @default(now()) @map("created_at")
  updatedAt       DateTime  @updatedAt @map("updated_at")
  isActive        Boolean   @default(true) @map("is_active")

  users           User[]
  profile         CompanyProfile?
  scores          BidScore[]
  decisions       PursuitDecision[]

  @@map("companies")
}

model CompanyProfile {
  id                    String   @id @default(uuid())
  companyId             String   @unique @map("company_id")
  expertise             String[]
  warehouseLocation     String   @map("warehouse_location")
  geographicReach       String[] @map("geographic_reach")
  budgetMin             Decimal  @map("budget_min") @db.Decimal(15, 2)
  budgetMax             Decimal  @map("budget_max") @db.Decimal(15, 2)
  preferredAgencies     String[] @map("preferred_agencies")
  preferredProcurement  String[] @map("preferred_procurement")
  createdAt             DateTime @default(now()) @map("created_at")
  updatedAt             DateTime @updatedAt @map("updated_at")

  company               Company  @relation(fields: [companyId], references: [id], onDelete: Cascade)

  @@map("company_profiles")
}

model BidOpportunity {
  id                String   @id @default(uuid())
  title             String
  description       String?
  category          String
  budget            Decimal  @db.Decimal(15, 2)
  procuringEntity   String   @map("procuring_entity")
  procurementMode   String   @map("procurement_mode")
  areaOfDelivery    String   @map("area_of_delivery")
  closingDate       DateTime @map("closing_date")
  deliveryDays      Int      @map("delivery_days")
  sourceUrl         String?  @map("source_url")
  status            String   @default("open")
  createdAt         DateTime @default(now()) @map("created_at")
  updatedAt         DateTime @updatedAt @map("updated_at")

  scores            BidScore[]
  decisions         PursuitDecision[]

  @@index([category])
  @@index([areaOfDelivery])
  @@index([closingDate])
  @@index([status])
  @@map("bid_opportunities")
}

model BidScore {
  id                  String   @id @default(uuid())
  bidId               String   @map("bid_id")
  companyId           String   @map("company_id")
  totalScore          Decimal  @map("total_score") @db.Decimal(5, 2)
  tier                String
  categoryMatch       Decimal  @map("category_match") @db.Decimal(5, 2)
  geoFeasibility      Decimal  @map("geo_feasibility") @db.Decimal(5, 2)
  budgetAlignment     Decimal  @map("budget_alignment") @db.Decimal(5, 2)
  agencyRelationship  Decimal  @map("agency_relationship") @db.Decimal(5, 2)
  procurementFit      Decimal  @map("procurement_fit") @db.Decimal(5, 2)
  timelineScore       Decimal  @map("timeline_score") @db.Decimal(5, 2)
  recommendation      String?
  concerns            String[]
  calculatedAt        DateTime @default(now()) @map("calculated_at")

  bid                 BidOpportunity @relation(fields: [bidId], references: [id], onDelete: Cascade)
  company             Company        @relation(fields: [companyId], references: [id], onDelete: Cascade)

  @@unique([bidId, companyId])
  @@index([bidId])
  @@index([companyId])
  @@index([tier])
  @@map("bid_scores")
}

model PursuitDecision {
  id          String   @id @default(uuid())
  bidId       String   @map("bid_id")
  companyId   String   @map("company_id")
  userId      String?  @map("user_id")
  decision    String
  notes       String?
  createdAt   DateTime @default(now()) @map("created_at")

  bid         BidOpportunity @relation(fields: [bidId], references: [id], onDelete: Cascade)
  company     Company        @relation(fields: [companyId], references: [id], onDelete: Cascade)
  user        User?          @relation(fields: [userId], references: [id], onDelete: SetNull)

  @@unique([bidId, companyId])
  @@index([bidId])
  @@index([companyId])
  @@index([userId])
  @@map("pursuit_decisions")
}

model DistanceMatrix {
  id            String  @id @default(uuid())
  fromLocation  String  @map("from_location")
  toLocation    String  @map("to_location")
  distanceKm    Decimal @map("distance_km") @db.Decimal(8, 2)

  @@unique([fromLocation, toLocation])
  @@index([fromLocation])
  @@index([toLocation])
  @@map("distance_matrix")
}
```

---

## Notes

1. **UUIDs**: Using UUIDs for primary keys to avoid enumeration attacks
2. **Indexes**: Strategic indexes on frequently queried fields
3. **Cascading**: Appropriate cascade deletes for data integrity
4. **Constraints**: Check constraints for data validation
5. **Arrays**: PostgreSQL array types for multi-value fields
6. **Timestamps**: All tables have audit timestamps
7. **Soft Deletes**: Users and companies use `is_active` flag

---

**Next Steps:**
- Choose ORM (Prisma vs SQL)
- Set up migrations
- Create seed data scripts
