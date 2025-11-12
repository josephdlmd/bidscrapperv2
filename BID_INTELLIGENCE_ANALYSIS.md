# BID INTELLIGENCE COMPLETE APPLICATION ANALYSIS

**Source File:** `/home/user/bidscrapperv2/bid-intelligence-complete.html`

---

## 1. DATA STRUCTURE DEFINITIONS

### Bid Opportunity Object
```javascript
{
  // Input Fields
  category: String,                      // Category of goods/services
  budget: Number,                        // Budget amount in PHP
  area_of_delivery: String,              // Delivery location/province
  opportunity_procuring_entity: String,  // Government agency/entity name
  opportunity_project_title: String,     // Project name/description
  procurement_mode: String,              // e.g., "public bidding", "shopping"
  closing_date: Date,                    // Bid closing date
  delivery_days: Number,                 // Required delivery timeline in days
  
  // Computed Fields (Output)
  score: Number,                         // Final calculated score (0-100)
  tier: String,                          // Classification: "priority", "review", "low"
  matchFactors: {
    categoryMatch: Number,               // 0-100
    geographicFeasibility: Number,       // 0-100
    budgetAlignment: Number,             // 0-100
    agencyRelationship: Number,          // 0-100
    procurementFit: Number,              // 0-100
    timeline: Number                     // 0-100
  },
  recommendation: String,                // Human-readable recommendation
  concerns: Array<String>                // Array of warning/concern messages
}
```

### Company Profile Object
```javascript
{
  id: String,                            // Unique company identifier
  name: String,                          // Company name
  expertise: Array<String>,              // Categories company specializes in
  warehouseLocation: String,             // Primary warehouse city
  geographicReach: Array<String>,        // List of provinces/areas served
  budgetRange: {
    min: Number,                         // Minimum contract value
    max: Number                          // Maximum contract value
  },
  preferredAgencies: Array<String>,      // List of preferred procuring agencies
  preferredProcurement: Array<String>    // List of preferred procurement modes
}
```

---

## 2. SCORING ALGORITHM DETAILS

### **EXACT CODE SNIPPETS FROM APPLICATION**

#### calculateCategoryMatch Function
```javascript
calculateCategoryMatch(e, t) {
  let n = e.toLowerCase();
  // Exact match: 100 points
  if (t.some(e => e.toLowerCase() === n)) return 100;
  
  // Partial/substring match: 75 points
  if (t.filter(e => {
    let t = e.toLowerCase();
    return n.includes(t) || t.includes(n)
  }).length > 0) return 75;
  
  // Related category mapping: 50 points
  for (let[e, r] of Object.entries({
    "medical supplies": ["healthcare", "emergency", "first aid", "ppe"],
    "emergency equipment": ["medical", "safety", "disaster", "rescue"],
    "it equipment": ["computer", "software", "technology", "office"],
    "construction materials": ["tools", "building", "infrastructure"],
    "food": ["catering", "prepared", "preserved", "meals"]
  }))
    if (t.some(t => t.toLowerCase().includes(e)) && 
        r.some(e => n.includes(e))) 
      return 50;
  
  // No match: 0 points
  return 0;
}
```

#### calculateGeographicFeasibility Function
```javascript
calculateGeographicFeasibility(e, t, n) {
  // Check if delivery area is in geographic reach
  if (n.some(t => e.includes(t) || t.includes(e))) {
    let n = this.calculateDistance(t, e);
    // Distance-based scoring
    return n <= 20 ? 100 :    // 0-20 km: excellent
           n <= 50 ? 85 :     // 21-50 km: good
           n <= 100 ? 70 :    // 51-100 km: moderate
           n <= 200 ? 50 : 30 // 101+ km: poor/very poor
  }
  // Outside service area: 10 points
  return 10;
}
```

#### calculateBudgetAlignment Function
```javascript
calculateBudgetAlignment(e, t) {
  // Case 1: Budget below minimum
  if (e < t.min) 
    return e >= .5 * t.min ? 40 : 20;
  
  // Case 2: Budget above maximum
  if (e > t.max) 
    return e <= 1.5 * t.max ? 50 : 20;
  
  // Case 3: Budget in range - check optimal range
  let n = 2 * t.min,      // Optimal minimum = 2x company min
      r = .7 * t.max;     // Optimal maximum = 70% of company max
  
  return e >= n && e <= r ? 100 : 75;  // 100 if in optimal, else 75
}
```

#### calculateAgencyRelationship Function
```javascript
calculateAgencyRelationship(e, t) {
  let n = e.toLowerCase();
  // Exact match: 100
  return t.some(e => e.toLowerCase() === n) ? 100 :
         // Partial match: 75
         t.some(e => n.includes(e.toLowerCase()) || 
                     e.toLowerCase().includes(n)) ? 75 :
         // Government type keywords: 50
         n.includes("department") || n.includes("bureau") || 
         n.includes("commission") || n.includes("university") ? 50 :
         // Default: 30
         30;
}
```

#### calculateProcurementFit Function
```javascript
calculateProcurementFit(e, t) {
  let n = e.toLowerCase();
  return t.some(e => e.toLowerCase() === n) ? 100 :         // Exact: 100
         t.some(e => n.includes(e.toLowerCase()) || 
                     e.toLowerCase().includes(n)) ? 75 :     // Partial: 75
         n.includes("small value") ? 80 :                    // Special: 80
         n.includes("shopping") ? 70 :                       // Special: 70
         n.includes("public bidding") || n.includes("competitive") ? 60 : // Special: 60
         40;  // Default: 40
}
```

#### calculateTimelineScore Function
```javascript
calculateTimelineScore(e, t) {
  let n = new Date,
      r = (new Date(e).getTime() - n.getTime()) / 864e5;  // Days until closing
  
  return r < 3 ? 30 :      // Less than 3 days: urgent (30)
         r < 7 ? 60 :      // 3-7 days: high priority (60)
         r >= 7 && r <= 21 ?
           t <= 30 ? 100 :  // 7-21 days, can deliver in 30 days: 100
           t <= 60 ? 85 :   // 7-21 days, can deliver in 60 days: 85
           70 :             // 7-21 days, delivery > 60 days: 70
         r > 60 ? 50 :      // More than 60 days: low (50)
         75;                // Default: 75
}
```

#### scoreBid Function (Main Scoring Engine)
```javascript
scoreBid(e, t) {
  let n, r = {
    categoryMatch: this.calculateCategoryMatch(e.category, t.expertise),
    geographicFeasibility: this.calculateGeographicFeasibility(
      e.area_of_delivery, t.warehouseLocation, t.geographicReach
    ),
    budgetAlignment: this.calculateBudgetAlignment(e.budget, t.budgetRange),
    agencyRelationship: this.calculateAgencyRelationship(
      e.opportunity_procuring_entity, t.preferredAgencies
    ),
    procurementFit: this.calculateProcurementFit(e.procurement_mode, t.preferredProcurement),
    timeline: this.calculateTimelineScore(e.closing_date, e.delivery_days)
  };
  
  // WEIGHTS - EXACT VALUES
  let a = {
    categoryMatch: .3,           // 30% weight
    geographicFeasibility: .25,  // 25% weight
    budgetAlignment: .2,         // 20% weight
    agencyRelationship: .1,      // 10% weight
    procurementFit: .1,          // 10% weight
    timeline: .05                // 5% weight
  };
  
  // Calculate weighted score
  let l = Object.entries(r).reduce((e, [t, n]) => e + n * a[t], 0);
  
  // CLASSIFICATION THRESHOLDS
  n = l >= 75 ? "priority" : l >= 50 ? "review" : "low";
  
  let i = "", o = [];
  
  // Generate recommendations and concerns
  if ("priority" === n)
    i = `Strong match: ${Math.round(r.categoryMatch)}% category alignment, favorable logistics and budget.`;
  else if ("review" === n) {
    i = "Moderate opportunity requiring evaluation of specific factors.";
    if (r.categoryMatch < 50) o.push("Category outside core expertise");
    if (r.geographicFeasibility < 50) o.push("Distant delivery location");
    if (r.budgetAlignment < 50) o.push("Budget outside optimal range");
  } else {
    i = "Low compatibility with current capabilities.";
    if (r.categoryMatch < 30) o.push("Unrelated category");
    if (r.geographicFeasibility < 30) o.push("Outside service area");
    if (r.budgetAlignment < 30) o.push("Budget mismatch");
  }
  
  // Add urgent warning if closing soon
  let s = (new Date(e.closing_date).getTime() - new Date().getTime()) / 864e5;
  if (s < 7 && s > 0)
    o.unshift(`⚠️ Closing in ${Math.ceil(s)} days`);
  
  return {
    ...e,
    score: Math.round(l),
    tier: n,
    matchFactors: r,
    recommendation: i,
    concerns: o
  };
}
```

---

## 3. CONSTANTS AND CONFIGURATION

### Score Weights
| Factor | Weight | Percentage |
|--------|--------|-----------|
| Category Match | 0.30 | 30% |
| Geographic Feasibility | 0.25 | 25% |
| Budget Alignment | 0.20 | 20% |
| Agency Relationship | 0.10 | 10% |
| Procurement Fit | 0.10 | 10% |
| Timeline | 0.05 | 5% |
| **Total** | **1.00** | **100%** |

### Classification Thresholds
```javascript
Priority: score >= 75
Review:   score >= 50 && score < 75
Low:      score < 50
```

### Distance Score Mapping
| Distance | Score |
|----------|-------|
| ≤ 20 km | 100 (Excellent) |
| 21-50 km | 85 (Good) |
| 51-100 km | 70 (Moderate) |
| 101-200 km | 50 (Poor) |
| > 200 km | 30 (Very Poor) |
| Outside reach | 10 (N/A) |

---

## 4. PHILIPPINE DISTANCE MATRIX

**Reference Data in kilometers (km)**

```javascript
{
  "Caloocan City": {
    "Metro Manila": 10, "Cavite": 35, "Bulacan": 25, "Rizal": 30,
    "Batangas": 90, "Pampanga": 75, "Camarines Sur": 350, "Bataan": 120
  },
  "Makati City": {
    "Metro Manila": 10, "Cavite": 25, "Bulacan": 35, "Rizal": 20,
    "Batangas": 85, "Pampanga": 85, "Camarines Sur": 360, "Bataan": 130
  },
  "Valenzuela City": {
    "Metro Manila": 10, "Cavite": 40, "Bulacan": 20, "Rizal": 35,
    "Batangas": 95, "Pampanga": 70, "Camarines Sur": 345, "Bataan": 115
  },
  "Quezon City": {
    "Metro Manila": 10, "Cavite": 30, "Bulacan": 30, "Rizal": 15,
    "Batangas": 85, "Pampanga": 80, "Camarines Sur": 355, "Bataan": 125
  }
}
```

### Distance Matrix Function
```javascript
calculateDistance(e, t) {
  let n = {
    "Caloocan City": {"Metro Manila": 10, "Cavite": 35, ...},
    "Makati City": {"Metro Manila": 10, "Cavite": 25, ...},
    "Valenzuela City": {"Metro Manila": 10, "Cavite": 40, ...},
    "Quezon City": {"Metro Manila": 10, "Cavite": 30, ...}
  };
  // If warehouse location not found, default to Caloocan City
  // If destination not found, default to 100 km
  return (n[e] || n["Caloocan City"])[t] || 100;
}
```

---

## 5. FILTER OPTIONS

### Available Filters in UI
1. **Category Filter**: `option value="all"` or specific category strings
2. **Location Filter**: `option value="all"` or specific area_of_delivery values
3. **Agency Filter**: `option value="all"` or specific opportunity_procuring_entity values
4. **Search Filter**: Text-based search on:
   - opportunity_project_title
   - opportunity_procuring_entity
   - category

### Filter Application Logic
```javascript
// Filter by category
if ("all" !== categoryFilter)
  bids = bids.filter(bid => bid.category === categoryFilter);

// Filter by location
if ("all" !== locationFilter)
  bids = bids.filter(bid => bid.area_of_delivery === locationFilter);

// Filter by agency
if ("all" !== agencyFilter)
  bids = bids.filter(bid => bid.opportunity_procuring_entity === agencyFilter);

// Text search (across multiple fields)
if (searchText !== "") {
  let searchLower = searchText.toLowerCase();
  bids = bids.filter(bid =>
    bid.opportunity_project_title.toLowerCase().includes(searchLower) ||
    bid.opportunity_procuring_entity.toLowerCase().includes(searchLower) ||
    bid.category.toLowerCase().includes(searchLower)
  );
}
```

---

## 6. CATEGORY MAPPING TABLE

For related category matching (50-point score):

| Primary Category | Related Keywords |
|-----------------|-----------------|
| medical supplies | healthcare, emergency, first aid, ppe |
| emergency equipment | medical, safety, disaster, rescue |
| it equipment | computer, software, technology, office |
| construction materials | tools, building, infrastructure |
| food | catering, prepared, preserved, meals |

---

## 7. TIMELINE CALCULATION DETAILS

**Formula:** `daysUntilClosing = (closingDate - today) / 864e5`

Where 864e5 = 86,400,000 milliseconds (1 day)

### Timeline Score Decision Tree
```
IF daysUntilClosing < 3
  → Return 30 (urgent: very close deadline)
ELSE IF daysUntilClosing < 7
  → Return 60 (high priority: closing within a week)
ELSE IF daysUntilClosing >= 7 AND daysUntilClosing <= 21
  → Return variable based on delivery_days:
     IF delivery_days <= 30: 100
     ELSE IF delivery_days <= 60: 85
     ELSE: 70
ELSE IF daysUntilClosing > 60
  → Return 50 (low priority: plenty of time)
ELSE
  → Return 75 (default)
```

---

## 8. BUDGET ALIGNMENT DECISION TREE

```
IF bid_budget < budgetRange.min
  IF bid_budget >= 0.5 * budgetRange.min
    → Score = 40
  ELSE
    → Score = 20

ELSE IF bid_budget > budgetRange.max
  IF bid_budget <= 1.5 * budgetRange.max
    → Score = 50
  ELSE
    → Score = 20

ELSE (bid_budget is in range)
  IF bid_budget >= (2 * budgetRange.min) AND 
     bid_budget <= (0.7 * budgetRange.max)
    → Score = 100 (in optimal range)
  ELSE
    → Score = 75 (in acceptable range)
```

---

## 9. FINAL SCORE CALCULATION EXAMPLE

**Example Bid:**
- category: "medical supplies"
- budget: 500,000
- area_of_delivery: "Cavite"
- opportunity_procuring_entity: "Department of Health"
- procurement_mode: "public bidding"
- closing_date: 7 days from today
- delivery_days: 25 days

**Company Profile:**
- expertise: ["medical supplies", "healthcare"]
- warehouseLocation: "Makati City"
- geographicReach: ["Metro Manila", "Cavite", "Rizal"]
- budgetRange: { min: 100,000, max: 1,000,000 }
- preferredAgencies: ["Department of Health", "Department of Education"]
- preferredProcurement: ["public bidding", "competitive"]

**Calculated Scores:**
- categoryMatch: 100 (exact match with expertise)
- geographicFeasibility: 85 (Makati to Cavite = 25km, within 21-50km range)
- budgetAlignment: 75 (in range but not optimal: 500k not in [200k-700k])
- agencyRelationship: 100 (exact match with preferred agency)
- procurementFit: 100 (exact match with preferred procurement)
- timeline: 100 (7 days, can deliver in 25 days)

**Final Score Calculation:**
```
finalScore = (100 × 0.30) + (85 × 0.25) + (75 × 0.20) + (100 × 0.10) + (100 × 0.10) + (100 × 0.05)
           = 30 + 21.25 + 15 + 10 + 10 + 5
           = 91.25
           ≈ 91 (rounded)
```

**Result:** PRIORITY TIER (score ≥ 75)

---

## 10. SOURCE CODE FILE LOCATION

**File Path:** `/home/user/bidscrapperv2/bid-intelligence-complete.html`

**Class:** `iv` (minified class containing all scoring logic)

**Key Methods:**
- `calculateDistance(warehouse, destination)`
- `calculateCategoryMatch(bidCategory, companyExpertise)`
- `calculateGeographicFeasibility(delivery, warehouse, reach)`
- `calculateBudgetAlignment(bidBudget, budgetRange)`
- `calculateAgencyRelationship(procuringEntity, preferredAgencies)`
- `calculateProcurementFit(procurementMode, preferredModes)`
- `calculateTimelineScore(closingDate, deliveryDays)`
- `scoreBid(bid, companyProfile)`

---

## 11. CONCERN/RECOMMENDATION THRESHOLDS

### Concerns are added if:

**For "Review" Tier:**
- categoryMatch < 50 → "Category outside core expertise"
- geographicFeasibility < 50 → "Distant delivery location"
- budgetAlignment < 50 → "Budget outside optimal range"

**For "Low" Tier:**
- categoryMatch < 30 → "Unrelated category"
- geographicFeasibility < 30 → "Outside service area"
- budgetAlignment < 30 → "Budget mismatch"

**Urgent Alert (Any Tier):**
- If 0 < daysUntilClosing < 7 → "⚠️ Closing in X days" (prepended to concerns)

---

**END OF ANALYSIS**
