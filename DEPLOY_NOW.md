# 🚀 DEPLOY YOUR APP NOW - Step by Step

**Your MongoDB is ready!** Let's get your app live in the next 15 minutes.

---

## ✅ Step 1: Push to GitHub (5 minutes)

### 1.1 Create GitHub Repository

1. Open: https://github.com/new
2. Fill in:
   - **Repository name**: `fraud-detection-system`
   - **Description**: `Quantum-Classical ML for Credit Card Fraud Detection - BE Project`
   - **Visibility**: Public (or Private if you prefer)
   - **❌ DO NOT check** "Add a README file"
3. Click **"Create repository"**

### 1.2 Get Your GitHub Username

Your GitHub URL will look like: `https://github.com/YOUR_USERNAME/fraud-detection-system`

**What's YOUR_USERNAME?** (write it down):
```
_______________________
```

### 1.3 Push Code

Copy and paste these commands **one by one** in your terminal:

```bash
cd "/Users/vishal.suthar/Downloads/BE Project"

# Add your repository (REPLACE YOUR_USERNAME with your actual username!)
git remote add origin https://github.com/YOUR_USERNAME/fraud-detection-system.git

# Push to GitHub
git push -u origin main
```

**If asked for password**: 
- Username: your GitHub username
- Password: Use a **Personal Access Token** (NOT your GitHub password)
  - Get it here: https://github.com/settings/tokens
  - Click **"Generate new token (classic)"**
  - Name it: `fraud-detection-deploy`
  - Check: ☑️ **repo** (full control)
  - Click **"Generate token"**
  - **COPY THE TOKEN** (you won't see it again!)
  - Use this token as your password

**✅ Done? Your code is now on GitHub!**

---

## ✅ Step 2: Deploy Backend to Render (5 minutes)

### 2.1 Sign Up

1. Go to: https://render.com
2. Click **"Get Started for Free"**
3. **Sign up with GitHub** (easiest option)
4. Click **"Authorize Render"**

### 2.2 Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Find and select your repository: **`fraud-detection-system`**
3. Click **"Connect"**

### 2.3 Configure Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `fraud-detection-api` |
| **Region** | Oregon (US West) or closest to you |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | **Free** |

### 2.4 Add Environment Variables

Scroll down to **"Environment Variables"** section:

1. Click **"Add Environment Variable"**
2. **Key**: `MONGODB_URL`
3. **Value**: 
   ```
   YOUR_MONGODB_CONNECTION_STRING_HERE
   ```
4. Click **"Add"**

### 2.5 Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes while it deploys
3. Watch the logs - look for: `Application startup complete`

### 2.6 Copy Your Backend URL

At the top of the page, you'll see your URL:
```
https://fraud-detection-api-XXXX.onrender.com
```

**Write it down here:**
```
_________________________________________________
```

**Test it**: Open that URL in browser, you should see:
```json
{"service": "Fraud Detection API", "status": "running", "models_loaded": true}
```

**✅ Backend is LIVE!**

---

## ✅ Step 3: Deploy Frontend to Vercel (3 minutes)

### 3.1 Sign Up

1. Go to: https://vercel.com/signup
2. Click **"Continue with GitHub"**
3. Click **"Authorize Vercel"**

### 3.2 Import Project

1. Click **"Add New..."** → **"Project"**
2. Find your repository: **`fraud-detection-system`**
3. Click **"Import"**

### 3.3 Configure Project

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Next.js` (auto-detected) |
| **Root Directory** | `frontend` (Click "Edit" and select) |
| **Build Command** | `npm run build` (default) |
| **Output Directory** | `.next` (default) |

### 3.4 Add Environment Variable

Click **"Environment Variables"**:

1. **Key**: `NEXT_PUBLIC_API_URL`
2. **Value**: Your Render URL from Step 2.6 (e.g., `https://fraud-detection-api-XXXX.onrender.com`)
3. Click **"Add"**

### 3.5 Deploy!

1. Click **"Deploy"**
2. Wait 2-3 minutes
3. You'll get a success screen with your URL!

**Your Frontend URL:**
```
https://fraud-detection-system-XXXX.vercel.app
```

**Write it down:**
```
_________________________________________________
```

**✅ Frontend is LIVE!**

---

## ✅ Step 4: Test Your Live App! (2 minutes)

1. **Open your Vercel URL** in browser

2. You should see the **Fraud Detection System** homepage

3. **Test with "Suspicious Transaction":**
   - Click **"Suspicious Transaction"** button
   - Click **"Check for Fraud"**
   - Wait 30-60 seconds (first request wakes up Render free tier)
   - Should see: **HIGH RISK ~87% fraud probability**

4. **Test with "Normal Transaction":**
   - Click **"Normal Transaction"** button
   - Click **"Check for Fraud"**
   - Should see: **LOW RISK ~20% fraud probability**

**🎉 If both work, YOUR APP IS FULLY LIVE!**

---

## 🐛 Troubleshooting

### Issue: Backend returns error

**Check Render logs:**
1. Go to Render dashboard
2. Click your service
3. Click **"Logs"** tab
4. Look for error messages

**Common fix**: MongoDB URL might be wrong format
- Should end with: `/fraud_detection?appName=Cluster0`
- Should have encoded password: `3110200322224%40Ait`

### Issue: Frontend can't connect to backend

**Check environment variable:**
1. Go to Vercel dashboard
2. Click your project → **Settings** → **Environment Variables**
3. Verify `NEXT_PUBLIC_API_URL` is correct
4. Should be your Render URL (from Step 2.6)

**If you changed it:**
1. Go to **Deployments** tab
2. Click **"..."** → **"Redeploy"**

### Issue: "CORS error" in browser console

**Fix backend CORS:**
1. Go to your GitHub repository
2. Edit `backend/main.py`
3. Find line 39: `allow_origins=["*"]`
4. Change to:
   ```python
   allow_origins=[
       "https://fraud-detection-system-xxxx.vercel.app",  # Your Vercel URL
       "http://localhost:3000"
   ]
   ```
5. Commit and push → Render will auto-redeploy

---

## 📝 Your Deployment Info

Fill this in as you complete each step:

```
✅ MongoDB Connection:
   YOUR_MONGODB_CONNECTION_STRING_HERE

✅ GitHub Repository:
   https://github.com/_____________/fraud-detection-system

✅ Backend URL (Render):
   https://fraud-detection-api-______________.onrender.com

✅ Frontend URL (Vercel):
   https://fraud-detection-system-______________.vercel.app

✅ API Documentation:
   [Your Backend URL]/docs
   https://fraud-detection-api-______________.onrender.com/docs
```

---

## 📊 For Your BE Project Presentation

### Share These Links:

```
🌐 Live Application:
   https://fraud-detection-system-______________.vercel.app

💻 GitHub Repository:
   https://github.com/_____________/fraud-detection-system

📚 API Documentation:
   https://fraud-detection-api-______________.onrender.com/docs
```

### Demo Script (3 minutes):

**Opening** (30 sec):
> "I've built a real-time fraud detection system using quantum-classical hybrid machine learning. It's deployed live on the cloud and can analyze credit card transactions instantly."

**Live Demo** (1 min):
1. Open your Vercel URL
2. Click "Suspicious Transaction"
3. Click "Check for Fraud"
4. Point out:
   - High fraud probability (87%)
   - Multiple model predictions (Classical, Quantum, Ensemble)
   - Risk factors identified
   - Recommendation to block

**Technical Innovation** (1 min):
> "The key innovation is the two-step feature selection: first using classical methods to reduce 69 features to 15, then quantum QSVM to select the final 6. This reduces quantum computation cost by 80% while achieving 96% ROC-AUC accuracy."

**Architecture** (30 sec):
> "It's a complete production system: Next.js frontend on Vercel, FastAPI backend on Render, MongoDB Atlas for storage. All deployed on cloud infrastructure with zero cost using free tiers."

---

## ✅ Final Checklist

- [ ] Code pushed to GitHub successfully
- [ ] Backend deployed on Render
- [ ] MongoDB URL added to Render env vars
- [ ] Backend URL works (shows API status)
- [ ] Frontend deployed on Vercel
- [ ] Backend URL added to Vercel env vars
- [ ] Frontend URL opens in browser
- [ ] "Suspicious Transaction" test works
- [ ] "Normal Transaction" test works
- [ ] Saved all URLs for presentation

**All checked? YOU'RE DONE! 🎉**

---

## 🔄 Making Updates Later

If you need to update your app:

```bash
# Make changes to your code
git add .
git commit -m "Description of changes"
git push origin main
```

**Both Vercel and Render will automatically redeploy!**

---

## 💰 Cost

**Everything is FREE:**
- ✅ MongoDB Atlas: Free tier (512 MB)
- ✅ Render: Free tier (750 hours/month)
- ✅ Vercel: Free tier (unlimited)

**Total: $0/month**

⚠️ **Note**: Render free tier sleeps after 15 min of inactivity. First request takes ~30 seconds to wake up. For your presentation, send a test request a minute before to wake it up!

---

## 🆘 Need Help?

1. **Check Render logs** for backend errors
2. **Check Vercel logs** for frontend errors  
3. **Verify all environment variables** are set correctly
4. **Make sure MongoDB URL** has `/fraud_detection` at the end

Still stuck? Read DEPLOYMENT.md for detailed troubleshooting.

---

<div align="center">

# 🚀 Ready? Let's Deploy!

**Start with Step 1 above ⬆️**

**Estimated time: 15 minutes**

You got this! 💪

</div>
