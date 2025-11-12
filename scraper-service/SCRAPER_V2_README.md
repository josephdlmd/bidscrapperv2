# PhilGEPS Scraper V2 - Updated Implementation

## 📋 Overview

This is an updated version of the PhilGEPS scraper based on analysis of actual PhilGEPS pages. The scraper now uses a **two-phase approach** to collect comprehensive bid data.

## 🎯 Key Changes

### 1. **Correct URL**
- ✅ Fixed URL to: `https://philgeps.gov.ph/BulletinBoard/view_more_current_oppourtunities`
- Previous (incorrect): `current_oppourtunities`

### 2. **Two-Phase Scraping Strategy**

#### **Phase 1: Build Index (Fast)**
- Scrapes list pages with pagination
- Collects basic bid information
- Extracts reference numbers and detail URLs
- **Does NOT include budget** (not available in list view)
- Handles pagination automatically (20 bids per page)

#### **Phase 2: Get Details (Comprehensive)**
- Fetches individual bid notice pages
- Extracts **Approved Budget for Contract (ABC)**
- Gets additional fields: delivery period, contact person, etc.
- Extracts line items with UNSPSC codes
- Progress tracking: "Processing bid X of Y..."

### 3. **Complete Field Mapping**

#### From List Page:
- `reference_number` - Unique bid ID
- `title` - Bid title
- `procurement_mode` - e.g., "Public Bidding"
- `classification` - Goods, Civil Works, Consulting Services, etc.
- `agency_name` - Procuring entity
- `publish_date` - When bid was published
- `closing_date` - Deadline for submissions
- `status` - e.g., "Published"
- `detail_url` - Link to full bid notice

#### From Detail Page (Additional):
- `approved_budget` - **ONLY available here!**
- `delivery_period` - e.g., "30 Day(s)"
- `delivery_location` - Province/area
- `contact_person` - Agency contact
- `control_number` - Internal tracking number
- `lot_type` - Single Lot, Multiple Lots
- `business_category` - Industry classification
- `funding_source` - Funding details
- `description` - Full HTML description
- `line_items[]` - Array of bid items with quantities

#### Line Items Structure:
```python
{
  "item_no": "1",
  "unspsc": "90101802",
  "lot_name": "Delivered meals services",
  "lot_description": "Delivered meals services",
  "quantity": "200",
  "unit_of_measure": "Pax"
}
```

### 4. **Correct CSS Selectors**

Uses `data-label` attributes for reliability:
```python
td[data-label="Bid Notice Reference Number"]
td[data-label="Notice Title"]
td[data-label="Mode of Procurement"]
td[data-label="Classification"]
td[data-label="Agency Name"]
td[data-label="Publish Date"]
td[data-label="Due Date"]
td[data-label="Status"]
```

## 🚀 Usage

### Basic Usage
```python
import asyncio
from scraper.philgeps_scraper import PhilGEPSScraper

async def main():
    scraper = PhilGEPSScraper()

    # Run full scrape (both phases)
    result = await scraper.run_daily_scrape()

    print(f"Total bids: {result['total_bids']}")
    print(f"Saved: {result['saved_count']}")

asyncio.run(main())
```

### Advanced Options

#### Limit Pages (Testing)
```python
# Only scrape first 2 pages
result = await scraper.run_daily_scrape(max_pages=2)
```

#### Skip Detail Fetching (Faster)
```python
# Only get list data, skip budget and line items
result = await scraper.run_daily_scrape(fetch_details=False)
```

#### Phase-by-Phase
```python
# Phase 1: Get list
bid_list = await scraper.scrape_current_opportunities_list()
print(f"Found {len(bid_list)} bids")

# Phase 2: Get details for specific bid
detail = await scraper.scrape_bid_detail(
    reference_number="7297",
    detail_url="https://philgeps.gov.ph/tenders/viewBidNotice/7297"
)
print(f"Budget: {detail['approved_budget']}")
```

## 💾 Database Setup

### For Local Testing (SQLite)
```bash
cd scraper-service
python setup_local_db_v2.py
```

### For Production (PostgreSQL)
```bash
psql -U your_user -d your_database -f migrations/001_philgeps_schema_v2.sql
```

## 📊 Database Schema

### Main Table: `bid_opportunities`
- All bid information from list and detail pages
- Primary key: `reference_number`
- Supports upsert (ON CONFLICT UPDATE)

### Related Table: `bid_line_items`
- Line items for each bid
- Foreign key to `bid_opportunities.reference_number`
- CASCADE delete when parent bid is removed

## 🔍 Reference Pages

The implementation is based on analysis of these saved pages:

1. **List Page**: `PhilGEPS Reference/PS-PhilGEPS.html`
   - Current opportunities listing
   - Shows: Page 1 of 5, 81 total records
   - 20 records per page

2. **Detail Page**: `PhilGEPS Reference/PS-PhilGEPS_Bid-Notice.html`
   - Bid Notice #7297
   - Full bid details including budget
   - Line items table

## ✅ Validation

The scraper correctly extracts:
- ✅ All 9 columns from list table
- ✅ Pagination info (page X of Y)
- ✅ Reference number as clickable link
- ✅ Approved Budget from detail page (70,000.00)
- ✅ Line items with UNSPSC codes
- ✅ All date fields with proper parsing

## 🎛️ Configuration

Set environment variables:
```bash
export PHILGEPS_USERNAME="your_username"
export PHILGEPS_PASSWORD="your_password"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
```

## 📝 Notes

- **Budget field** is ONLY available in detail pages, not in list view
- Pagination starts at page 1 (no `?page=` parameter)
- Subsequent pages use: `?page=N&direction=Tenders.tender_start_datetime+desc`
- The scraper maintains persistent browser profile to avoid CAPTCHAs
- Line items table may have multiple entries per bid

## 🔄 Migration from V1

If you have existing V1 data:
1. The new schema is incompatible (different field names)
2. Run the migration script to recreate tables
3. Re-scrape data using V2 scraper
4. Old fields like `procuring_entity` → `agency_name`
5. Old fields like `area_of_delivery` → `delivery_location`

## 🐛 Troubleshooting

### "No bids found"
- Check if still logged in (session may expire)
- Verify correct URL is being used
- Check CSS selectors match current page structure

### "Budget is None"
- Budget is only in detail pages
- Make sure `fetch_details=True` in run_daily_scrape()
- Check detail page scraping is working

### Database errors
- Run migration script to create/update schema
- Verify all columns exist in database
- Check DATABASE_URL is correct

## 📚 Further Reading

- PhilGEPS Official Site: https://philgeps.gov.ph
- UNSPSC Codes: https://www.unspsc.org
- Scrapling Documentation: https://github.com/D4Vinci/Scrapling
