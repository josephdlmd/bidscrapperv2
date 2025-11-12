/**
 * Sample data for testing and initial app state
 */

import type { CompanyProfile, BidOpportunity } from '@/types'

// Default company profile
export const defaultCompany: CompanyProfile = {
  id: 'company-1',
  name: 'Sample Medical Supplies Corp',
  expertise: ['medical supplies', 'healthcare', 'ppe', 'emergency equipment'],
  warehouseLocation: 'Makati City',
  geographicReach: ['Metro Manila', 'Cavite', 'Rizal', 'Bulacan', 'Batangas'],
  budgetRange: {
    min: 100000,
    max: 5000000
  },
  preferredAgencies: [
    'Department of Health',
    'Department of Education',
    'Armed Forces of the Philippines',
    'Philippine National Police'
  ],
  preferredProcurement: [
    'public bidding',
    'competitive bidding',
    'shopping',
    'small value procurement'
  ],
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01')
}

// Sample bid opportunities
export const sampleBids: BidOpportunity[] = [
  {
    id: 'bid-1',
    title: 'Supply and Delivery of Medical Equipment and Supplies',
    description: 'Procurement of various medical equipment and supplies for regional hospital',
    category: 'medical supplies',
    budget: 500000,
    procuringEntity: 'Department of Health',
    procurementMode: 'public bidding',
    areaOfDelivery: 'Cavite',
    closingDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // 14 days from now
    deliveryDays: 30,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-2',
    title: 'PPE and Safety Equipment for Hospital Staff',
    description: 'Personal protective equipment including masks, gloves, face shields',
    category: 'ppe',
    budget: 750000,
    procuringEntity: 'Department of Health - Region IV',
    procurementMode: 'competitive bidding',
    areaOfDelivery: 'Metro Manila',
    closingDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
    deliveryDays: 21,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-3',
    title: 'School Furniture and Fixtures',
    description: 'Student desks, chairs, and classroom equipment',
    category: 'furniture',
    budget: 1200000,
    procuringEntity: 'Department of Education',
    procurementMode: 'public bidding',
    areaOfDelivery: 'Bulacan',
    closingDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000), // 21 days from now
    deliveryDays: 45,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-4',
    title: 'Emergency Medical Response Equipment',
    description: 'Ambulance equipment, stretchers, first aid kits',
    category: 'emergency equipment',
    budget: 350000,
    procuringEntity: 'Philippine National Police',
    procurementMode: 'shopping',
    areaOfDelivery: 'Metro Manila',
    closingDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000), // 5 days from now
    deliveryDays: 15,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-5',
    title: 'IT Equipment and Computer Supplies',
    description: 'Desktop computers, laptops, printers for government office',
    category: 'it equipment',
    budget: 2500000,
    procuringEntity: 'Department of Trade and Industry',
    procurementMode: 'public bidding',
    areaOfDelivery: 'Rizal',
    closingDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days from now
    deliveryDays: 60,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-6',
    title: 'Hospital Bedding and Linens',
    description: 'Bed sheets, pillow cases, blankets for hospital use',
    category: 'medical supplies',
    budget: 180000,
    procuringEntity: 'Department of Health',
    procurementMode: 'small value procurement',
    areaOfDelivery: 'Cavite',
    closingDate: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000), // 10 days from now
    deliveryDays: 20,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-7',
    title: 'Construction Materials for School Building Renovation',
    description: 'Cement, steel bars, paint, and other construction materials',
    category: 'construction materials',
    budget: 5500000,
    procuringEntity: 'Department of Education - Division of Bulacan',
    procurementMode: 'public bidding',
    areaOfDelivery: 'Bulacan',
    closingDate: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000), // 45 days from now
    deliveryDays: 90,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-8',
    title: 'Laboratory Equipment and Supplies',
    description: 'Chemistry and biology lab equipment for public high school',
    category: 'medical supplies',
    budget: 850000,
    procuringEntity: 'Department of Education',
    procurementMode: 'competitive bidding',
    areaOfDelivery: 'Metro Manila',
    closingDate: new Date(Date.now() + 18 * 24 * 60 * 60 * 1000), // 18 days from now
    deliveryDays: 35,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-9',
    title: 'Surgical Instruments and Tools',
    description: 'Various surgical instruments for operating room',
    category: 'medical supplies',
    budget: 1500000,
    procuringEntity: 'Armed Forces of the Philippines',
    procurementMode: 'public bidding',
    areaOfDelivery: 'Metro Manila',
    closingDate: new Date(Date.now() + 25 * 24 * 60 * 60 * 1000), // 25 days from now
    deliveryDays: 40,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-10',
    title: 'Office Supplies and Materials',
    description: 'Paper, pens, folders, and general office supplies',
    category: 'office supplies',
    budget: 95000,
    procuringEntity: 'Department of Agriculture',
    procurementMode: 'shopping',
    areaOfDelivery: 'Batangas',
    closingDate: new Date(Date.now() + 8 * 24 * 60 * 60 * 1000), // 8 days from now
    deliveryDays: 10,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-11',
    title: 'First Aid and Emergency Medical Kits',
    description: 'Comprehensive first aid kits for police stations',
    category: 'emergency equipment',
    budget: 220000,
    procuringEntity: 'Philippine National Police',
    procurementMode: 'shopping',
    areaOfDelivery: 'Rizal',
    closingDate: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000), // 6 days from now
    deliveryDays: 12,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-12',
    title: 'Janitorial and Cleaning Supplies',
    description: 'Disinfectants, mops, brooms, cleaning agents',
    category: 'cleaning supplies',
    budget: 150000,
    procuringEntity: 'Department of Health',
    procurementMode: 'small value procurement',
    areaOfDelivery: 'Metro Manila',
    closingDate: new Date(Date.now() + 12 * 24 * 60 * 60 * 1000), // 12 days from now
    deliveryDays: 15,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-13',
    title: 'Medical Diagnostic Equipment',
    description: 'X-ray machine, ultrasound, ECG equipment',
    category: 'medical supplies',
    budget: 3500000,
    procuringEntity: 'Department of Health - Regional Hospital',
    procurementMode: 'public bidding',
    areaOfDelivery: 'Pampanga',
    closingDate: new Date(Date.now() + 40 * 24 * 60 * 60 * 1000), // 40 days from now
    deliveryDays: 75,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-14',
    title: 'Disaster Relief Supplies',
    description: 'Emergency food packs, water, tents, blankets',
    category: 'emergency equipment',
    budget: 2800000,
    procuringEntity: 'Department of Social Welfare and Development',
    procurementMode: 'public bidding',
    areaOfDelivery: 'Metro Manila',
    closingDate: new Date(Date.now() + 15 * 24 * 60 * 60 * 1000), // 15 days from now
    deliveryDays: 25,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-15',
    title: 'Pharmaceutical Medicines and Drugs',
    description: 'Essential medicines for public health center',
    category: 'medical supplies',
    budget: 890000,
    procuringEntity: 'Department of Health',
    procurementMode: 'competitive bidding',
    areaOfDelivery: 'Cavite',
    closingDate: new Date(Date.now() + 20 * 24 * 60 * 60 * 1000), // 20 days from now
    deliveryDays: 30,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-16',
    title: 'Sports Equipment and Athletic Gear',
    description: 'Basketball hoops, volleyballs, sports uniforms',
    category: 'sports equipment',
    budget: 450000,
    procuringEntity: 'Department of Education',
    procurementMode: 'shopping',
    areaOfDelivery: 'Bulacan',
    closingDate: new Date(Date.now() + 11 * 24 * 60 * 60 * 1000), // 11 days from now
    deliveryDays: 20,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-17',
    title: 'Fire Safety Equipment',
    description: 'Fire extinguishers, smoke detectors, fire alarms',
    category: 'safety equipment',
    budget: 680000,
    procuringEntity: 'Bureau of Fire Protection',
    procurementMode: 'competitive bidding',
    areaOfDelivery: 'Metro Manila',
    closingDate: new Date(Date.now() + 16 * 24 * 60 * 60 * 1000), // 16 days from now
    deliveryDays: 28,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-18',
    title: 'Catering Services for Government Event',
    description: 'Food and beverage catering for 500 participants',
    category: 'food',
    budget: 320000,
    procuringEntity: 'Department of Tourism',
    procurementMode: 'shopping',
    areaOfDelivery: 'Rizal',
    closingDate: new Date(Date.now() + 9 * 24 * 60 * 60 * 1000), // 9 days from now
    deliveryDays: 5,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-19',
    title: 'Vehicle Spare Parts and Accessories',
    description: 'Automotive spare parts for government vehicles',
    category: 'automotive',
    budget: 1100000,
    procuringEntity: 'Department of Transportation',
    procurementMode: 'public bidding',
    areaOfDelivery: 'Metro Manila',
    closingDate: new Date(Date.now() + 35 * 24 * 60 * 60 * 1000), // 35 days from now
    deliveryDays: 50,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  },
  {
    id: 'bid-20',
    title: 'Maternal and Child Health Supplies',
    description: 'Pre-natal vitamins, baby formula, health supplies',
    category: 'medical supplies',
    budget: 560000,
    procuringEntity: 'Department of Health',
    procurementMode: 'competitive bidding',
    areaOfDelivery: 'Batangas',
    closingDate: new Date(Date.now() + 22 * 24 * 60 * 60 * 1000), // 22 days from now
    deliveryDays: 32,
    sourceUrl: 'https://www.philgeps.gov.ph',
    status: 'open',
    createdAt: new Date()
  }
]

// Initialize app with sample data
export function initializeSampleData() {
  if (typeof window === 'undefined') return

  const { getCompanies, getBids, saveCompany, saveBids } = require('@/lib/storage/localStorage')

  // Only initialize if no data exists
  const existingCompanies = getCompanies()
  const existingBids = getBids()

  if (existingCompanies.length === 0) {
    saveCompany(defaultCompany)
    console.log('✅ Initialized default company')
  }

  if (existingBids.length === 0) {
    saveBids(sampleBids)
    console.log(`✅ Initialized ${sampleBids.length} sample bids`)
  }
}
