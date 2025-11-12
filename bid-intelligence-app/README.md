# Bid Intelligence Platform

A comprehensive bid scoring and management application for Philippine government procurement opportunities. Features intelligent 6-factor scoring, localStorage persistence, and real-time analytics.

## 🚀 Quick Deploy to Vercel

### Option 1: Deploy via GitHub (Recommended)

1. **Push this project to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Vercel-ready bid intelligence app"
   git push
   ```

2. **Go to [Vercel](https://vercel.com)**
   - Sign in with your GitHub account
   - Click "Add New Project"
   - Import your repository
   - **Important**: Set the root directory to `bid-intelligence-app`
   - Click "Deploy"

3. **Done!** Your app will be live in ~2 minutes at `https://your-app.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   cd bid-intelligence-app
   vercel
   ```

3. **Follow the prompts**:
   - Set up and deploy? **Y**
   - Which scope? (Select your account)
   - Link to existing project? **N**
   - Project name? (Press enter for default)
   - Directory? **.**
   - Override settings? **N**

4. **Production Deploy**:
   ```bash
   vercel --prod
   ```

## 🏃 Run Locally

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. **Install dependencies**:
   ```bash
   cd bid-intelligence-app
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Open browser**:
   ```
   http://localhost:3000
   ```

### Build for Production

```bash
npm run build
npm start
```

## 📦 What's Included

### Features
- ✅ **6-Factor Scoring Algorithm**
  - Category Match (30%)
  - Geographic Feasibility (25%)
  - Budget Alignment (20%)
  - Agency Relationship (10%)
  - Procurement Fit (10%)
  - Timeline Score (5%)

- ✅ **3-Tier Classification**
  - Priority: ≥75 (High-value opportunities)
  - Review: 50-74 (Medium potential)
  - Low: <50 (Lower priority)

- ✅ **Complete Dashboard**
  - Real-time KPIs
  - Top 5 priority bids
  - Score distribution charts
  - Decision analytics

- ✅ **Smart Filtering**
  - Search by title, entity, category
  - Filter by location and tier
  - Sort by score

- ✅ **Company Profile Management**
  - Expertise areas
  - Geographic reach
  - Budget preferences
  - Agency relationships
  - Auto-rescore on profile changes

- ✅ **Decision Tracking**
  - Pursue/Pass decisions
  - Full decision history
  - Export to CSV

- ✅ **Sample Data**
  - 20 realistic Philippine government bids
  - Pre-configured company profile
  - Ready to test immediately

### Tech Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand (minimal usage)
- **Storage**: localStorage (browser-based)
- **Icons**: lucide-react
- **Dates**: date-fns

### Project Structure
```
bid-intelligence-app/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Dashboard
│   │   ├── opportunities/        # Main bid list
│   │   ├── companies/            # Profile editor
│   │   ├── analytics/            # Charts & stats
│   │   ├── history/              # Decision timeline
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Global styles
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx        # Top navigation
│   │   │   └── Sidebar.tsx       # Left menu
│   │   ├── features/
│   │   │   ├── BidTable.tsx      # Bid cards
│   │   │   └── ScoreBreakdown.tsx # Score modal
│   │   └── ui/                   # shadcn components
│   ├── lib/
│   │   ├── scoring/
│   │   │   └── BidScorer.ts      # 6-factor algorithm
│   │   ├── storage/
│   │   │   └── localStorage.ts   # CRUD operations
│   │   ├── data/
│   │   │   └── sampleData.ts     # 20 sample bids
│   │   └── utils.ts              # Helpers, CSV export
│   └── types/
│       └── index.ts              # TypeScript interfaces
├── package.json
├── next.config.js
├── tsconfig.json
├── tailwind.config.ts
└── vercel.json
```

## 🎯 Usage Guide

### 1. Customize Your Profile
Go to **Companies** page and update:
- Company name
- Expertise areas (comma-separated)
- Warehouse location
- Geographic reach
- Budget range
- Preferred agencies
- Preferred procurement modes

All bids will automatically rescore based on your profile!

### 2. Browse Opportunities
Navigate to **Opportunities** to:
- View all scored bids
- Filter by category, location, tier
- Search by keywords
- See detailed score breakdowns
- Make Pursue/Pass decisions

### 3. Make Decisions
Click **Pursue** or **Pass** on any bid to:
- Track your decisions
- View decision history
- Export priority bids to CSV

### 4. View Analytics
Check **Analytics** page for:
- Score distribution charts
- Decision breakdown (Pursue vs Pass)
- Top categories and locations
- Total and pursued bid values

### 5. Review History
Visit **History** page to see:
- Chronological decision timeline
- Bid details with scores
- Filter by decision type

## 🔧 Configuration

### Environment Variables
No environment variables needed! The app uses localStorage for persistence.

### localStorage Keys
- `bid_companies`: Company profiles
- `bid_opportunities`: All bids
- `bid_scores`: Calculated scores
- `bid_decisions`: Pursue/Pass decisions

### Reset Data
Open browser console and run:
```javascript
localStorage.clear()
location.reload()
```

## 🚢 Deployment Notes

### Vercel Configuration
- **Framework**: Next.js (auto-detected)
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`

### Important for Vercel
When importing from GitHub:
1. **Set Root Directory**: `bid-intelligence-app`
2. All other settings can remain default
3. Vercel will automatically detect Next.js configuration

### Environment
No environment variables required. The app runs entirely in the browser with localStorage.

## 📊 Sample Data

The app comes with 20 pre-loaded Philippine government bid opportunities including:
- Medical supplies (PPE, pharmaceuticals, equipment)
- IT services and hardware
- Office supplies
- Construction materials
- Emergency equipment
- Educational materials

All bids include:
- Realistic budgets (₱100K - ₱5M)
- Various procurement modes
- Philippine locations
- Real government agencies
- Appropriate timelines

## 🛠️ Troubleshooting

### Build fails on Vercel
- Check that root directory is set to `bid-intelligence-app`
- Verify package.json dependencies are correct
- Check build logs for specific errors

### "Module not found" errors
```bash
npm install
```

### Styles not loading
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Check that globals.css is present in src/app/
- Verify Tailwind config is correct

### localStorage not persisting
- Check browser privacy settings
- Disable private/incognito mode
- Clear browser cache and reload

### Scores not calculating
- Open browser console and check for errors
- Verify company profile is saved
- Try resetting localStorage and reloading

## 🎨 Customization

### Add More Bid Sources
Edit `src/lib/data/sampleData.ts` to add more sample bids or integrate with real APIs.

### Modify Scoring Algorithm
Edit `src/lib/scoring/BidScorer.ts` to adjust:
- Factor weights
- Distance calculations
- Budget scoring curves
- Timeline scoring logic

### Change UI Theme
Edit `tailwind.config.ts` to customize:
- Colors
- Typography
- Spacing
- Border radius

### Add Backend Integration
When ready to add Supabase or another backend:
1. Install Supabase client
2. Replace localStorage functions in `src/lib/storage/`
3. Add authentication
4. Update API endpoints

## 📝 License

MIT License - Feel free to use for commercial or personal projects.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code documentation
3. Test with sample data first

---

**Built with ❤️ for Philippine government procurement professionals**
