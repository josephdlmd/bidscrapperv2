-- Migration: PhilGEPS Schema V2
-- Date: 2025-11-12
-- Description: Update schema based on PhilGEPS reference pages analysis
--              Adds all fields from list view and detail view
--              Supports two-phase scraping strategy

-- Drop existing tables if they exist (clean migration)
DROP TABLE IF EXISTS bid_line_items CASCADE;
DROP TABLE IF EXISTS bid_opportunities CASCADE;

-- Create main bid_opportunities table
CREATE TABLE bid_opportunities (
    id SERIAL PRIMARY KEY,

    -- Core identification
    reference_number VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    status VARCHAR(50),

    -- URLs
    detail_url TEXT,
    source_url TEXT,

    -- Procurement details
    procurement_mode VARCHAR(200),
    classification VARCHAR(100),  -- Goods, Civil Works, Consulting Services, etc.
    lot_type VARCHAR(50),
    control_number VARCHAR(100),

    -- Financial
    approved_budget DECIMAL(15,2),  -- From detail page only!

    -- Dates
    publish_date TIMESTAMP,
    closing_date TIMESTAMP,
    date_created TIMESTAMP,
    date_last_updated TIMESTAMP,

    -- Agency/Organization
    agency_name TEXT,
    client_agency TEXT,
    contact_person VARCHAR(255),

    -- Location and delivery
    delivery_location TEXT,
    delivery_period VARCHAR(100),

    -- Categorization
    business_category TEXT,
    funding_source TEXT,
    applicable_rules TEXT,

    -- Additional info
    bid_validity_period VARCHAR(50),
    description TEXT,  -- Full HTML description

    -- Metadata
    scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create line items table
CREATE TABLE bid_line_items (
    id SERIAL PRIMARY KEY,
    reference_number VARCHAR(50) NOT NULL,
    item_no VARCHAR(20),
    unspsc VARCHAR(50),  -- United Nations Standard Products and Services Code
    lot_name TEXT,
    lot_description TEXT,
    quantity VARCHAR(50),
    unit_of_measure VARCHAR(50),

    CONSTRAINT fk_reference_number
        FOREIGN KEY (reference_number)
        REFERENCES bid_opportunities(reference_number)
        ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_bid_reference_number ON bid_opportunities(reference_number);
CREATE INDEX idx_bid_closing_date ON bid_opportunities(closing_date);
CREATE INDEX idx_bid_classification ON bid_opportunities(classification);
CREATE INDEX idx_bid_agency_name ON bid_opportunities(agency_name);
CREATE INDEX idx_bid_status ON bid_opportunities(status);
CREATE INDEX idx_bid_publish_date ON bid_opportunities(publish_date);
CREATE INDEX idx_line_items_ref ON bid_line_items(reference_number);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_bid_opportunities_updated_at
    BEFORE UPDATE ON bid_opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE bid_opportunities IS 'PhilGEPS bid opportunities scraped from view_more_current_oppourtunities and detail pages';
COMMENT ON TABLE bid_line_items IS 'Line items for each bid opportunity';
COMMENT ON COLUMN bid_opportunities.reference_number IS 'Unique bid notice reference number from PhilGEPS';
COMMENT ON COLUMN bid_opportunities.approved_budget IS 'Approved Budget for Contract (ABC) - only available from detail page';
COMMENT ON COLUMN bid_opportunities.classification IS 'Bid classification: Goods, Civil Works, Consulting Services, etc.';
COMMENT ON COLUMN bid_line_items.unspsc IS 'United Nations Standard Products and Services Code';
