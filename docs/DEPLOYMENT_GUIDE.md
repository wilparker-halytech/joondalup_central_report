# Streamlit Cloud Deployment Guide

Complete step-by-step instructions for deploying the Illuminator Billing Processor to Streamlit Cloud.

---

## Prerequisites

✅ GitHub account (free) - https://github.com
✅ Streamlit Cloud account (free) - https://share.streamlit.io

**Time Required:** 10-15 minutes

---

## STEP 1: Create GitHub Account (if you don't have one)

1. Go to https://github.com
2. Click "Sign up"
3. Follow the registration process
4. Verify your email

**Skip this if you already have a GitHub account**

---

## STEP 2: Create New GitHub Repository

1. Log into GitHub
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in:
   - **Repository name:** `illuminator-billing` (or your choice)
   - **Description:** "Illuminator Central billing processor"
   - **Visibility:** ✅ **Public** (required for free Streamlit Cloud)
   - ✅ Check **"Add a README file"**
4. Click **"Create repository"**

**You now have an empty GitHub repo!**

---

## STEP 3: Upload Your Files to GitHub

### Option A: Web Upload (Easiest)

1. On your new repository page, click **"Add file"** → **"Upload files"**
2. Drag these files from your computer:
   - `streamlit_app.py` (the main app)
   - `requirements.txt` (dependencies)
   - `README.md` (documentation)
   - `.gitignore` (optional)
3. Add commit message: "Initial commit - billing processor app"
4. Click **"Commit changes"**

### Option B: Git Command Line (If you know Git)

```bash
# Navigate to your project folder
cd /path/to/your/files

# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit - billing processor app"

# Connect to GitHub
git remote add origin https://github.com/YOUR-USERNAME/illuminator-billing.git

# Push
git branch -M main
git push -u origin main
```

**Your code is now on GitHub!**

---

## STEP 4: Sign Up for Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click **"Sign up"**
3. Click **"Continue with GitHub"**
4. Authorize Streamlit to access your GitHub account
5. You'll be taken to the Streamlit Cloud dashboard

**This is 100% free - no credit card required**

---

## STEP 5: Deploy Your App

1. On Streamlit Cloud dashboard, click **"New app"**
2. Fill in the deployment form:
   - **Repository:** Select `YOUR-USERNAME/illuminator-billing`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** Choose a subdomain (e.g., `coj-billing.streamlit.app`)
3. Click **"Advanced settings"** (optional):
   - Python version: 3.11 (recommended)
   - Leave other settings as default
4. Click **"Deploy!"**

**Deployment will take 2-3 minutes**

You'll see:
- "Your app is being deployed..."
- Build logs scrolling by
- "Your app is live!" when complete

---

## STEP 6: Test Your App

1. Once deployed, you'll see your app URL: `https://your-app.streamlit.app`
2. Test it:
   - Upload a sample Illuminator CSV file
   - Verify it processes correctly
   - Check the output
   - Test the download

**Your app is now live and publicly accessible!**

---

## STEP 7: Add Password Protection (Optional but Recommended)

To protect your app:

1. In your GitHub repo, create a new file: `.streamlit/secrets.toml`
2. Add this content:
   ```toml
   [passwords]
   admin = "your-password-here"
   ```
3. In `streamlit_app.py`, add at the top (after imports):
   ```python
   import streamlit as st
   
   # Password protection
   def check_password():
       if "password_correct" not in st.session_state:
           st.text_input("Password", type="password", key="password")
           if st.button("Login"):
               if st.session_state.password == st.secrets["passwords"]["admin"]:
                   st.session_state.password_correct = True
                   st.rerun()
               else:
                   st.error("Incorrect password")
           return False
       return True
   
   if not check_password():
       st.stop()
   ```
4. Commit and push changes
5. Streamlit Cloud will auto-redeploy (takes 1-2 min)

---

## STEP 8: Share with City of Joondalup

Send them:
- App URL: `https://your-app.streamlit.app`
- Password (if you set one)
- Quick start instructions:
  1. Upload Illuminator CSV export
  2. Adjust rate if needed
  3. Download processed billing file

---

## Updating the App

When you need to make changes:

1. Edit files in your GitHub repo (click the file → pencil icon)
2. Commit the changes
3. Streamlit Cloud **automatically redeploys** within 1-2 minutes

**No manual deployment needed!**

---

## Monitoring & Maintenance

### View App Logs
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "Manage app" → "Logs"

### Check Usage
- Streamlit Cloud shows:
  - Number of users
  - Usage metrics
  - Uptime

### Free Tier Limits
- **1 GB storage**
- **1 GB RAM**
- **Unlimited users**
- **99.9% uptime**
- Apps may "sleep" after inactivity (wake up in ~30 seconds)

---

## Troubleshooting

### "App failed to deploy"
**Solution:** Check the logs for errors
- Usually missing dependency in requirements.txt
- Or Python syntax error

### "Module not found"
**Solution:** Add missing package to requirements.txt

### "App is slow"
**Solution:** 
- Free tier has limited resources
- Upgrade to Teams plan ($20/month) if needed
- Or optimize code

### "Can't access secrets"
**Solution:**
1. Go to Streamlit Cloud dashboard
2. Click your app → "Settings" → "Secrets"
3. Add secrets there (don't commit secrets.toml to public repos)

---

## Alternative: Run Locally

If you don't want to deploy publicly:

1. Install Python 3.11+
2. Open terminal/command prompt
3. Navigate to project folder
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run app:
   ```bash
   streamlit run streamlit_app.py
   ```
6. App opens in browser at `http://localhost:8501`

**This runs on your local machine only**

---

## Cost Summary

| Service | Cost | Notes |
|---------|------|-------|
| GitHub (public repo) | **FREE** | Unlimited repos |
| Streamlit Cloud | **FREE** | 1 app, unlimited users |
| Custom domain | $12/year | Optional (e.g., billing.coj.gov.au) |
| **TOTAL** | **$0** | Can run entirely free |

---

## Next Steps

1. ✅ Deploy the app (Steps 1-6)
2. ✅ Test with real data
3. ✅ Add password protection (Step 7)
4. ✅ Update scenario mappings for all CoJ facilities
5. ✅ Set correct billing rate
6. ✅ Share with CoJ staff
7. Monitor usage and gather feedback

---

## Support Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Community:** https://discuss.streamlit.io
- **GitHub Docs:** https://docs.github.com
- **This Project:** Issues tab on GitHub repo

---

## Files Needed for Deployment

Make sure you have these 3 files in your GitHub repo:

1. ✅ **streamlit_app.py** - Main application code
2. ✅ **requirements.txt** - Python dependencies
3. ✅ **README.md** - Documentation (optional but recommended)

Optional:
4. **.gitignore** - Excludes unnecessary files
5. **.streamlit/secrets.toml** - For passwords (don't commit if public repo!)

---

**That's it! You now have a production-ready web app for $0/month.**

Questions? Check the Troubleshooting section above or open an issue on GitHub.