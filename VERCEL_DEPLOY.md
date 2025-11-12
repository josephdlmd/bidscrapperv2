# 🚀 Vercel Deployment Guide

## ⚠️ CRITICAL: Root Directory Configuration

The **#1 reason for 404 errors** is incorrect root directory setting. Follow these steps exactly:

## Step-by-Step Deployment

### 1. Go to Vercel Dashboard
- Visit [vercel.com/new](https://vercel.com/new)
- Sign in with your GitHub account

### 2. Import Repository
- Click "Import Git Repository"
- Select: `josephdlmd/bidscrapperv2`
- Click "Import"

### 3. Configure Project ⚠️ MOST IMPORTANT STEP
**Before clicking Deploy, you MUST configure the root directory:**

1. Click on "Root Directory" section
2. Click "Edit"
3. Select or type: `bid-intelligence-app`
4. Click "Continue"

**Screenshot of what to look for:**
```
Root Directory: bid-intelligence-app  ✅ MUST BE SET
Framework Preset: Next.js (auto-detected)
Build Command: npm run build (auto-detected)
Output Directory: .next (auto-detected)
Install Command: npm install (auto-detected)
```

### 4. Deploy
- Click "Deploy"
- Wait 2-3 minutes for build to complete

### 5. Visit Your Live Site
- Vercel will provide a URL: `https://your-project.vercel.app`
- The app should load with the dashboard and 20 sample bids

---

## 🔧 Troubleshooting 404 Errors

### Error: 404 NOT_FOUND

**Cause**: Root directory not set to `bid-intelligence-app`

**Fix**:
1. Go to your project in Vercel dashboard
2. Click "Settings"
3. Click "General"
4. Scroll to "Root Directory"
5. Click "Edit"
6. Enter: `bid-intelligence-app`
7. Click "Save"
8. Go to "Deployments" tab
9. Click "⋯" (three dots) on latest deployment
10. Click "Redeploy"

### Error: Build Failed

**Check the build logs** in Vercel:
1. Go to Deployments
2. Click on the failed deployment
3. Click "Build Logs"
4. Look for errors

Common fixes:
- Ensure all dependencies are in package.json
- Check for TypeScript errors
- Verify all imports are correct

### Error: Module Not Found

**Cause**: Dependencies not installed

**Fix**: Redeploy the project (Vercel will reinstall)

---

## ✅ Verification Checklist

After deployment, verify:
- [ ] Home page (Dashboard) loads with KPIs
- [ ] Opportunities page shows 20 bids
- [ ] Companies page loads profile editor
- [ ] Analytics page shows charts
- [ ] History page is accessible
- [ ] Navigation works between pages
- [ ] Bids are scored and sorted
- [ ] Can make Pursue/Pass decisions
- [ ] localStorage persists data

---

## 🔄 Redeploying After Changes

If you make code changes:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```

2. **Vercel auto-deploys** on every push to the branch

Or manually trigger:
1. Go to Vercel dashboard
2. Click "Deployments"
3. Click "⋯" on latest
4. Click "Redeploy"

---

## 📊 Expected Build Output

Successful build should show:
```
✓ Creating an optimized production build
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (5/5)
✓ Finalizing page optimization

Route (app)                              Size
┌ ○ /                                    5.2 kB
├ ○ /analytics                           3.8 kB
├ ○ /companies                           4.1 kB
├ ○ /history                             2.9 kB
└ ○ /opportunities                       6.3 kB
```

---

## 🆘 Still Getting 404?

**Double-check these settings in Vercel:**

1. **Root Directory**: Must be `bid-intelligence-app`
2. **Framework**: Should auto-detect as "Next.js"
3. **Node Version**: Should be 18.x or higher
4. **Environment Variables**: None required (we use localStorage)

**If still broken:**
1. Delete the project in Vercel
2. Re-import from GitHub
3. Set root directory to `bid-intelligence-app` BEFORE deploying
4. Deploy again

---

## 📝 Quick Reference

| Setting | Value |
|---------|-------|
| Root Directory | `bid-intelligence-app` |
| Framework | Next.js (auto) |
| Build Command | `npm run build` (auto) |
| Output Directory | `.next` (auto) |
| Install Command | `npm install` (auto) |
| Node Version | 18.x+ (auto) |

---

**Need more help?** Check the build logs in Vercel dashboard for specific errors.
