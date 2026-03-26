# 🚀 SNAP Deployment - Quick Reference Card

## 📋 Before You Start

```
✓ GitHub account (free at github.com)
✓ Render account (free at render.com)  
✓ Supabase account (free at supabase.com)
✓ Git installed on computer
✓ App working locally: python app.py
```

---

## 🔑 Key Files Needed

| File | Purpose | Status |
|------|---------|--------|
| `app.py` | Main Flask application | ✓ Required |
| `requirements.txt` | Dependencies | ✓ Required |
| `Procfile` | Deployment config | ✓ Required |
| `runtime.txt` | Python version | ✓ Required |
| `.env` | Local environment vars | ✓ Don't commit! |
| `.env.example` | Template (in GitHub) | ✓ Reference |
| `.gitignore` | Files to skip in Git | ✓ Has .env |

---

## 🔐 Environment Variables

**Local (.env file):**
```
DATABASE_URL=postgresql://postgres:PASS@db.PROJECT.supabase.co:5432/postgres
FLASK_ENV=production
SECRET_KEY=your-random-key-from-randomkeygen.com
FLASK_DEBUG=False
PORT=5000
```

**Render dashboard (Environment section):**
- Same variables as above
- `DB URL`, `FLASK_ENV`, `SECRET_KEY`, `FLASK_DEBUG`

---

## 📊 Supabase Setup (5 min)

1. Create project at supabase.com
2. Get connection string: Settings → Database → URI
3. Run `setup.sql` in SQL Editor
4. Copy connection string → save for Step 5

---

## 📦 GitHub Push (5 min)

```bash
# Check .env is NOT listed
git status

# Commit and push
git add .
git commit -m "Ready for deployment"
git push origin main
```

**Verify:** Code visible on github.com/USERNAME/snap-price-comparison

---

## 🚀 Render Deploy (10 min)

1. Create Web Service at render.com
2. Connect GitHub repo: `snap-price-comparison`
3. Fill settings:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
4. Add environment variables (see above)
5. Click "Create Web Service"
6. Wait for deployment ✓

**Live URL:** https://snap-price-comparison.onrender.com

---

## ✅ Test Deployment

| Test | Command | Expected |
|------|---------|----------|
| Homepage | https://snap-price-comparison.onrender.com | SNAP logo visible |
| API | https://snap-price-comparison.onrender.com/all_products | JSON response |
| Search | https://snap-price-comparison.onrender.com/price/iPhone | JSON with products |

---

## ⚠️ Common Mistakes (Don't Do These!)

| ❌ Mistake | ✅ Fix |
|-----------|--------|
| Push .env to GitHub | Add .env to .gitignore |
| Hardcode credentials | Use os.getenv('VAR_NAME') |
| localhost in production code | Use 0.0.0.0 and PORT env var |
| Forget Procfile | Create: `web: gunicorn app:app` |
| Don't test locally first | Run `python app.py` before push |
| Wrong DATABASE_URL | Verify in Supabase → Settings |
| No error handling | Try-except all database calls |
| Old Python version | Use Python 3.9+, specify in runtime.txt |

---

## 🆘 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Build fails | Check Render logs, fix error, git push |
| Blank page | Check browser console (F12), test /all_products |
| No data showing | Run setup.sql in Supabase SQL Editor |
| Database connection error | Verify DATABASE_URL in Render env |
| Static files broken | Check templates/ and static/ folders exist |
| "Port already in use" | Kill process: `taskkill /PID <PID> /F` |

---

## 📱 Redeploy After Changes

```bash
# Make changes locally and test
python app.py

# Push to GitHub (auto-deploys to Render)
git add .
git commit -m "your message"
git push origin main

# Watch Render logs for deployment status
```

---

## 📞 Important Links

- **Supabase Connection:** Settings → Database
- **Render Logs:** Dashboard → Logs tab
- **GitHub Repo:** github.com/USERNAME/snap-price-comparison
- **Live App:** https://snap-price-comparison.onrender.com

---

## 🎯 Deployment Timeline

| Phase | Time | Status |
|-------|------|--------|
| Prepare project locally | 5 min | Before deployment |
| Supabase setup | 5 min | Before deployment |
| Push to GitHub | 2 min | Before deployment |
| Render deployment | 10 min | Watch logs |
| Test live app | 5 min | Verify everything |
| **Total** | **~30 min** | ✓ Live! |

---

## 💡 Pro Tips

✅ Test `test_connection.py` before pushing
```bash
python test_connection.py
```

✅ Keep changes small, deploy often
- Small commits = easy to debug if something breaks

✅ Monitor logs regularly
- Render → Logs tab check for errors/issues

✅ Backup database regularly
- Supabase → Backups

✅ Use .env.example as template
- Commit .env.example to GitHub (without secrets)
- Never commit actual .env file

---

## 📖 Full Guides

- **Complete Setup:** See `DEPLOYMENT_GUIDE.md`
- **Step-by-Step Render:** See `RENDER_DEPLOYMENT_CHECKLIST.md`
- **Project Info:** See `README.md`

---

## 🎉 Success Checklist

- [ ] App running locally
- [ ] Supabase database created & tables set up
- [ ] CODE pushed to GitHub (not .env!)
- [ ] Render deployment complete
- [ ] Live URL loads correctly
- [ ] API endpoints working
- [ ] Database connected
- [ ] No errors in logs

**You're deployed! 🚀**
