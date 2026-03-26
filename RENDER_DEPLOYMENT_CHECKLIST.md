# Render Deployment Checklist - Step by Step

Follow these exact steps to deploy your SNAP application on Render.

## ✅ Phase 1: Pre-Deployment Setup (Local Machine)

### Step 1: Verify Local Setup
- [ ] Navigate to project folder: `cd d:\SCET\S4\DBMS\ARSHA\price-comparison-project02-main`
- [ ] Virtual environment activated
- [ ] Run app locally: `python app.py`
- [ ] Visit http://localhost:5000 - should work ✓
- [ ] App shows products from database

### Step 2: Verify All Files Exist
Run this command in project root:
```bash
dir /s /b | findstr "Procfile requirements.txt .env app.py"
```

Check list:
- [ ] `Procfile` (exactly this name, no extension)
- [ ] `requirements.txt` (contains Flask, gunicorn, psycopg2)
- [ ] `.env` (created locally - NOT committed)
- [ ] `app.py` (main Flask file)
- [ ] `runtime.txt` (contains `python-3.11.7`)
- [ ] `.gitignore` (includes `.env`)

### Step 3: Create/Update Configuration Files

**Check Procfile:**
```bash
cat Procfile
```
Should show: `web: gunicorn app:app`

**Check requirements.txt:**
```bash
cat requirements.txt
```
Should include at minimum:
```
Flask==3.1.3
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

**Check .env exists:**
```bash
dir .env
```
Should exist (if not, create it with your DATABASE_URL)

---

## ✅ Phase 2: Version Control Setup (GitHub)

### Step 4: Initialize Git (If Not Already Done)

```bash
# Check if git is initialized
git status
```

If error "fatal: not a git repository":
```bash
git init
git config user.name "Your Name"
git config user.email "your.email@gmail.com"
```

### Step 5: Verify .gitignore

```bash
cat .gitignore | findstr ".env"
```

**Should show:** `.env` in the list

If not found, add it:
```bash
echo .env >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

### Step 6: Pre-deployment Git Check

Run this BEFORE committing:
```bash
git status
```

**Check:**
- [ ] `.env` is NOT in the list (if listed, you'll expose secrets!)
- [ ] All other files listed are correct
- [ ] No `.env` anywhere in list

**If .env is listed:**
```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

### Step 7: First Commit

```bash
git add .
git status  # Verify .env not listed
git commit -m "Initial commit: SNAP price comparison system ready for deployment"
```

### Step 8: Create GitHub Repository

1. Go to https://github.com/new
2. Create new repository:
   - **Name:** `snap-price-comparison`
   - **Description:** Deployment ready
   - **Public or Private:** Your choice
3. Click **Create repository**
4. Copy the ssh or https URL

### Step 9: Connect to GitHub & Push

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/snap-price-comparison.git
git branch -M main
git push -u origin main
```

**Verify:**
- [ ] Go to https://github.com/YOUR_USERNAME/snap-price-comparison
- [ ] You should see your code
- [ ] `.env` file is NOT there (good!)

---

## ✅ Phase 3: Supabase Database Setup

### Step 10: Create Supabase Project

1. Go to https://supabase.com
2. Click **Sign Up** → Use GitHub
3. Click **New Project**
4. Fill in:
   - **Project name:** `snap-prod` (or your choice)
   - **Database password:** Create strong password (SAVE THIS!)
   - **Region:** Closest to you
5. Click **Create new project**
6. Wait 2-3 minutes...

### Step 11: Get Connection String

1. Go to **Settings** (bottom left)
2. Click **Database**
3. Look for **Connection String**
4. Click **URI** tab
5. Copy the connection string (looks like this):
   ```
   postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
   ```

**SAVE THIS! You'll need it next.**

### Step 12: Create Tables in Supabase

1. Go to **SQL Editor** (left sidebar)
2. Click **New Query**
3. Copy & paste ALL of your `setup.sql` file content
4. Click **Run** (green play button)
5. Should show ✓ Success

---

## ✅ Phase 4: Render Deployment

### Step 13: Create Render Account

1. Go to https://render.com
2. Click **Sign Up**
3. Choose **GitHub** (authorize it)
4. Click **Dashboard**

### Step 14: Connect GitHub to Render

1. Click **Settings** (top right)
2. Click **Connected Services**
3. Click **Connect GitHub**
4. Authorize Render
5. Grant access to your repository

### Step 15: Create Web Service on Render

1. Click **New +** (top left)
2. Click **Web Service**
3. Select your repository: `snap-price-comparison`
4. Click **Connect**

### Step 16: Configure Deployment Settings

Fill in these exact fields:

| Field | Value |
|-------|-------|
| **Name** | `snap-price-comparison` |
| **Region** | `Ohio` (or closest) |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Auto-deploy** | On |

### Step 17: Add Environment Variables

1. Find **Environment** section (scroll down)
2. Click **Add Environment Variable**
3. Add each variable:

**Variable 1:**
- **Key:** `DATABASE_URL`
- **Value:** Paste your Supabase connection string from Step 11
  - Example: `postgresql://postgres:password@db.xyz.supabase.co:5432/postgres`
  - **IMPORTANT:** Make sure password is correct!

**Variable 2:**
- **Key:** `FLASK_ENV`
- **Value:** `production`

**Variable 3:**
- **Key:** `SECRET_KEY`
- **Value:** Generate from https://randomkeygen.com/ (copy any 32+ character key)

**Variable 4:**
- **Key:** `FLASK_DEBUG`
- **Value:** `False`

### Step 18: Select Plan

1. Scroll to bottom
2. Select **Free** plan (or Starter)
3. Click **Create Web Service**

### Step 19: Monitor Deployment

Render will now deploy! Wait for:

1. **Build Log** - Should show:
   ```
   ✓ Building Docker image
   ✓ Database migration...
   ✓ Installing dependencies
   ```

2. **Deploy Log** - Should show:
   ```
   ✓ Deploy live
   ✓ Listening on 0.0.0.0:10000
   ```

3. Should take 3-5 minutes total

---

## ✅ Phase 5: Testing Deployment

### Step 20: Find Your Live URL

After deployment completes:
1. Go to Render dashboard
2. Click on your service: `snap-price-comparison`
3. Look for **Deployed URL** (top right)
4. It looks like: `https://snap-price-comparison.onrender.com`

### Step 21: Test Homepage

1. Copy your URL from Step 20
2. Open in browser: `https://snap-price-comparison.onrender.com/`
3. **Should see:**
   - [ ] SNAP logo in navbar
   - [ ] Search box visible
   - [ ] Login button visible
   - [ ] Product grid (if you added data)
   - [ ] No error messages

### Step 22: Test API Endpoints

**Test 1: All Products**
```
https://snap-price-comparison.onrender.com/all_products
```
Should return JSON with products

**Test 2: Search Product**
```
https://snap-price-comparison.onrender.com/price/iPhone
```
Should return matching products in JSON

**Test 3: Check Logs**
1. Go to Render dashboard
2. Click **Logs** tab
3. Should show your requests
4. No error messages

---

## ✅ Phase 6: Troubleshooting

### Problem: App says "Build failed"

**Solution:**
1. Click on the red error message
2. Scroll to see exact error
3. Common fixes:
   - Missing package in `requirements.txt` → Add it → Push to GitHub → Redeploy
   - Syntax error in `app.py` → Fix locally → Test → Push → Redeploy
   - Python version mismatch → Update `runtime.txt` → Redeploy

**Redeploy:**
```bash
git add .
git commit -m "Fix: deployment error"
git push origin main
# Render auto-deploys!
```

### Problem: "Deployment live" but blank page

**Solution:**
1. Check browser console (F12 → Console)
2. Look for errors
3. Common issues:
   - Static files path wrong
   - DATABASE_URL not set
   - Database tables not created

**Test database:**
Visit: `https://snap-price-comparison.onrender.com/all_products`
- If JSON returns → Database works ✓
- If error → Check DATABASE_URL in Render environment

### Problem: "Database connection refused"

**Solution:**
1. Go to Render → Environment
2. Find `DATABASE_URL`
3. Verify it's correct (check Supabase password)
4. In Supabase → SQL Editor, run: `SELECT 1`
5. If Supabase works, try: Click **Logs** in Render to see exact error

### Problem: Static files not loading (CSS/JS broken)

**Solution:**
1. Check folder structure is correct:
   ```
   templates/       (contains HTML files)
   static/          (contains css/js files)
   app.py           (at root)
   ```
2. In `app.py`, verify:
   ```python
   app = Flask(__name__,
       template_folder='templates',
       static_folder='static'
   )
   ```
3. Redeploy after any file structure changes

---

## ✅ Phase 7: Maintenance & Monitoring

### Weekly Tasks
- [ ] Check Render logs for errors
- [ ] Monitor database storage usage in Supabase
- [ ] Test app in browser (homepage loads)

### Monthly Tasks
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Backup Supabase database
- [ ] Review Render logs for performance

### Deployment Cycle
1. Make code changes locally
2. Test: `python app.py`
3. Commit: `git add . && git commit -m "message"`
4. Push: `git push origin main`
5. Render auto-deploys! (watch logs)

---

## ✅ Final Verification Checklist

Before declaring deployment "DONE", verify:

- [ ] App loads at `https://snap-price-comparison.onrender.com`
- [ ] Homepage shows SNAP branding
- [ ] Products load from database
- [ ] Search works
- [ ] API endpoint `/all_products` returns JSON
- [ ] No error messages in browser
- [ ] Render logs show no errors
- [ ] Database connection working
- [ ] `.env` not visible on GitHub

---

## 🎉 Deployment Complete!

Your app is now live on the internet!

**Your live URL:** https://snap-price-comparison.onrender.com

**Next Steps:**
1. Add real product data to Supabase
2. Test login/signup functionality
3. Monitor logs for issues
4. Add more features
5. Share with others!

---

## 📞 Quick Help

**Common Commands:**

```bash
# Check git status
git status

# View build logs
# → Go to Render dashboard → Click service → Logs

# Test database locally
python test_connection.py

# Redeploy after code change
git add .
git commit -m "your message"
git push origin main
# Render auto-deploys in 1-2 minutes
```

**Get Help:**
- Render Docs: https://render.com/docs
- Supabase Docs: https://supabase.com/docs
- Flask Docs: https://flask.palletsprojects.com/
- GitHub Issues: https://github.com/YOUR_USERNAME/snap-price-comparison/issues

Good luck! 🚀
