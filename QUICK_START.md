# ⚡ Quick Start Guide

Get your fraud detection system up and running in 10 minutes!

---

## 🎯 What You Need

1. **MongoDB Connection String** - I'll help you set this up
2. **GitHub Account** - To host code
3. **10 minutes** ⏱️

---

## 📝 Step-by-Step Instructions

### Step 1: MongoDB Setup (5 minutes)

1. **Go to MongoDB Atlas**: https://www.mongodb.com/cloud/atlas/register

2. **Sign up** for free account (can use Google sign-in)

3. **Create a FREE cluster**:
   - Click "Build a Database"
   - Choose **FREE** tier (M0 Sandbox)
   - Select cloud provider (AWS recommended)
   - Choose region closest to you
   - Click "Create"
   - Wait 3-5 minutes ⏳

4. **Create Database User**:
   - Click "Database Access" (left sidebar)
   - Click "Add New Database User"
   - Username: `frauduser`
   - Password: Click "Autogenerate Secure Password" → **COPY AND SAVE THIS!**
   - Role: "Read and write to any database"
   - Click "Add User"

5. **Allow Network Access**:
   - Click "Network Access" (left sidebar)
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere"
   - Click "Confirm"

6. **Get Connection String**:
   - Click "Database" (left sidebar)
   - Click "Connect" button
   - Choose "Connect your application"
   - **COPY** the connection string (looks like):
     ```
     mongodb+srv://frauduser:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   - Replace `<password>` with your saved password
   - Add `/fraud_detection` before the `?`:
     ```
     mongodb+srv://frauduser:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/fraud_detection?retryWrites=true&w=majority
     ```

**✅ SAVE THIS FULL CONNECTION STRING! You'll paste it in Step 3.**

---

### Step 2: Push to GitHub (2 minutes)

1. **Create GitHub Repository**:
   - Go to: https://github.com/new
   - Name: `fraud-detection-system`
   - **Public** (or Private if you prefer)
   - **Do NOT** check "Add README"
   - Click "Create repository"

2. **Get Your Repository URL**:
   - Copy the URL shown (looks like): 
     ```
     https://github.com/YOUR_USERNAME/fraud-detection-system.git
     ```

3. **Push Code** (run in terminal):

   ```bash
   cd "/Users/vishal.suthar/Downloads/BE Project"
   
   # Add your GitHub repository
   git remote add origin https://github.com/YOUR_USERNAME/fraud-detection-system.git
   
   # Push code
   git push -u origin main
   ```

   If asked for password, use a **Personal Access Token**:
   - Get at: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Check "repo" scope
   - Copy token and use as password

**✅ Code is now on GitHub!**

---

### Step 3: Deploy Backend to Render (2 minutes)

1. **Sign up at Render**:
   - Go to: https://render.com
   - Click "Get Started for Free"
   - **Sign up with GitHub** (easiest)
   - Authorize Render

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Select your repository: `fraud-detection-system`
   - Configure:
     - **Name**: `fraud-detection-api`
     - **Branch**: `main`
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: **Free**

3. **Add Environment Variables**:
   - In "Environment" section, click "Add Environment Variable"
   - **Key**: `MONGODB_URL`
   - **Value**: **PASTE YOUR MONGODB CONNECTION STRING** from Step 1
   - Click "Add"

4. **Deploy**:
   - Click "Create Web Service"
   - Wait 5-10 minutes (watch logs)
   - When you see "Application startup complete" → ✅ DONE!

5. **Copy Your Backend URL**:
   - At top of page, copy URL (looks like):
     ```
     https://fraud-detection-api-xxxx.onrender.com
     ```
   - **SAVE THIS! You need it for next step.**

---

### Step 4: Deploy Frontend to Vercel (1 minute)

1. **Sign up at Vercel**:
   - Go to: https://vercel.com/signup
   - **Sign up with GitHub**
   - Authorize Vercel

2. **Import Project**:
   - Click "Add New" → "Project"
   - Select `fraud-detection-system` repository
   - Configure:
     - **Framework**: Next.js
     - **Root Directory**: `frontend`
     - Click "Edit" next to Build Command if needed

3. **Add Environment Variable**:
   - Click "Environment Variables"
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: **PASTE YOUR BACKEND URL** from Step 3 (from Render)
   - Click "Add"

4. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - You'll get a URL like: `https://fraud-detection-system-xxx.vercel.app`

**🎉 YOUR APP IS LIVE!**

---

## ✅ Test Your App

1. **Open your Vercel URL** in browser

2. **Click "Suspicious Transaction"** preset button

3. **Click "Check for Fraud"**

4. **See the result!**
   - Should show HIGH RISK with ~87% fraud probability
   - See predictions from all three models
   - See risk factors

**If it works → YOU'RE DONE! 🚀**

---

## 🐛 Troubleshooting

### Backend not working?

**Test backend directly**:
- Visit: `https://your-backend-url.onrender.com/`
- Should see: `{"service": "Fraud Detection API", "status": "running"}`

**If you see error**:
1. Go to Render Dashboard → Your Service → Logs
2. Look for error messages
3. Common issues:
   - MongoDB connection string wrong → Check Step 1.6
   - Missing environment variable → Check Step 3.3

### Frontend shows error?

1. Check backend URL in Vercel:
   - Vercel Dashboard → Your Project → Settings → Environment Variables
   - Make sure `NEXT_PUBLIC_API_URL` is correct
   - Should be your Render URL (from Step 3.5)

2. **Redeploy** if you changed env vars:
   - Vercel Dashboard → Deployments → Click "..." → Redeploy

### CORS Error in browser console?

Update backend to allow your frontend domain:

1. Edit `backend/main.py` on GitHub
2. Change line 39 from:
   ```python
   allow_origins=["*"]
   ```
   to:
   ```python
   allow_origins=["https://your-frontend.vercel.app", "http://localhost:3000"]
   ```
3. Commit and push → Render will auto-redeploy

---

## 📋 Your Deployment Info

Fill this in as you go:

```
✅ MongoDB Connection String:
   mongodb+srv://frauduser:_____________@cluster0._____.mongodb.net/fraud_detection?...

✅ GitHub Repository:
   https://github.com/____________/fraud-detection-system

✅ Backend URL (Render):
   https://fraud-detection-api-________.onrender.com

✅ Frontend URL (Vercel):
   https://fraud-detection-system-________.vercel.app
```

---

## 🎓 For Your Presentation

**Share these links**:
1. **Live App**: Your Vercel URL
2. **GitHub**: Your repository URL
3. **API Docs**: Your Backend URL + `/docs`

**Demo Script**:
1. Open live app
2. Click "Suspicious Transaction" → Submit
3. Show HIGH RISK result
4. Click "Normal Transaction" → Submit  
5. Show LOW RISK result
6. Explain: "Uses quantum-classical hybrid ML for 96% accuracy"

---

## 💰 Cost

**Everything is FREE!**
- MongoDB Atlas: Free tier (512MB)
- Render: Free tier (750 hours/month)
- Vercel: Free tier (unlimited)

⚠️ **Note**: Render free tier sleeps after 15 min idle. First request takes ~30 sec to wake up.

---

## 🆘 Still Stuck?

Common commands:

```bash
# View backend logs
# Go to Render Dashboard → Your Service → Logs

# Test backend locally
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Test frontend locally
cd frontend
npm install
npm run dev
```

**Need help?** Check DEPLOYMENT.md for detailed troubleshooting.

---

## ✅ Done Checklist

- [ ] MongoDB cluster created
- [ ] Database user created with password saved
- [ ] Connection string copied
- [ ] Code pushed to GitHub
- [ ] Backend deployed on Render
- [ ] MONGODB_URL added to Render
- [ ] Backend URL copied
- [ ] Frontend deployed on Vercel
- [ ] NEXT_PUBLIC_API_URL added to Vercel
- [ ] Live app tested successfully

**All checked? Congratulations! Your project is LIVE! 🎉**
