# 🚀 Deployment Guide - Fraud Detection System

Complete guide to deploy your Quantum-Classical Fraud Detection system to production.

---

## 📋 Prerequisites

1. **GitHub Account** - To host your code
2. **MongoDB Atlas Account** - For database (free tier available)
3. **Vercel Account** - For frontend deployment (free)
4. **Render Account** - For backend deployment (free tier available)

---

## Step 1: Setup MongoDB Atlas

### 1.1 Create Account and Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new **FREE** cluster (M0 Sandbox)
4. Choose a cloud provider and region (closest to you)
5. Wait 3-5 minutes for cluster to be created

### 1.2 Configure Database Access

1. Click **Database Access** in left sidebar
2. Click **Add New Database User**
3. Choose **Password** authentication
4. Username: `frauduser`
5. Password: (Generate a secure password - SAVE THIS!)
6. User Privileges: **Read and write to any database**
7. Click **Add User**

### 1.3 Configure Network Access

1. Click **Network Access** in left sidebar
2. Click **Add IP Address**
3. Click **Allow Access from Anywhere** (0.0.0.0/0)
   - For production, restrict to your backend server IP
4. Click **Confirm**

### 1.4 Get Connection String

1. Click **Database** in left sidebar
2. Click **Connect** on your cluster
3. Choose **Connect your application**
4. Copy the connection string (looks like):
   ```
   mongodb+srv://frauduser:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with the password you created
6. Add database name at the end: `...mongodb.net/fraud_detection?retryWrites...`

**Your final connection string should look like:**
```
mongodb+srv://frauduser:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/fraud_detection?retryWrites=true&w=majority
```

**SAVE THIS CONNECTION STRING!** You'll need it for the backend.

---

## Step 2: Push Code to GitHub

### 2.1 Create Repository

1. Go to [GitHub](https://github.com)
2. Click **New Repository**
3. Name: `fraud-detection-system`
4. Description: `Quantum-Classical ML for Credit Card Fraud Detection`
5. **Public** or **Private** (your choice)
6. **DO NOT** initialize with README (we already have one)
7. Click **Create Repository**

### 2.2 Push Code

Open terminal in your project directory and run:

```bash
cd "/Users/vishal.suthar/Downloads/BE Project"

# Add all files
git add .

# Commit
git commit -m "Initial commit: Fullstack fraud detection system"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/fraud-detection-system.git

# Push
git push -u origin main
```

If asked for credentials:
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your password)
  - Get token at: https://github.com/settings/tokens
  - Click **Generate new token (classic)**
  - Check **repo** scope
  - Copy and save the token

---

## Step 3: Deploy Backend to Render

### 3.1 Create Account

1. Go to [Render](https://render.com)
2. Sign up with GitHub (easiest)
3. Authorize Render to access your repositories

### 3.2 Create Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repository `fraud-detection-system`
3. Configure:
   - **Name**: `fraud-detection-api`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

### 3.3 Add Environment Variables

In the Environment section, add:

| Key | Value |
|-----|-------|
| `MONGODB_URL` | (Paste your MongoDB connection string from Step 1.4) |
| `IBM_QUANTUM_TOKEN` | (Optional - leave empty for now) |

### 3.4 Deploy

1. Click **Create Web Service**
2. Wait 5-10 minutes for deployment
3. You'll see logs scrolling - wait for "Application startup complete"
4. Copy your backend URL (looks like): `https://fraud-detection-api.onrender.com`

**SAVE THIS URL!** You'll need it for the frontend.

---

## Step 4: Deploy Frontend to Vercel

### 4.1 Create Account

1. Go to [Vercel](https://vercel.com)
2. Sign up with GitHub (easiest)
3. Authorize Vercel to access your repositories

### 4.2 Import Project

1. Click **Add New** → **Project**
2. Select your repository `fraud-detection-system`
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 4.3 Add Environment Variables

Click **Environment Variables** and add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | (Paste your Render backend URL from Step 3.4) |

Example:
```
NEXT_PUBLIC_API_URL=https://fraud-detection-api.onrender.com
```

### 4.4 Deploy

1. Click **Deploy**
2. Wait 2-3 minutes for build
3. You'll get a URL like: `https://fraud-detection-system.vercel.app`

**🎉 Your app is now LIVE!**

---

## Step 5: Test Your Deployed App

1. Open your Vercel URL in browser
2. Fill out the transaction form (or use presets)
3. Click "Check for Fraud"
4. You should see predictions!

### Troubleshooting

**If predictions don't work:**

1. **Check Backend Logs**:
   - Go to Render dashboard
   - Click your service → Logs tab
   - Look for errors

2. **Common Issues**:

   - **CORS Error**: Backend needs to allow your frontend domain
     ```python
     # In backend/main.py, update:
     allow_origins=["https://your-frontend.vercel.app"]
     ```

   - **MongoDB Connection Failed**: Check connection string format
   - **Backend URL Wrong**: Make sure NEXT_PUBLIC_API_URL is correct

3. **Test Backend Directly**:
   - Visit: `https://your-backend.onrender.com/`
   - Should see: `{"service": "Fraud Detection API", "status": "running"}`

---

## Step 6: (Optional) Custom Domain

### For Vercel (Frontend):
1. Go to Vercel dashboard → Your project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### For Render (Backend):
1. Render free tier doesn't support custom domains
2. Upgrade to paid plan if needed

---

## 🔄 Future Updates

When you make code changes:

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push origin main
```

Both Vercel and Render will **automatically redeploy** when you push to GitHub!

---

## 📊 Monitoring

### Backend (Render):
- View logs: Render Dashboard → Your Service → Logs
- Monitor usage: Render Dashboard → Metrics

### Frontend (Vercel):
- Analytics: Vercel Dashboard → Your Project → Analytics
- View logs: Vercel Dashboard → Deployments → Click deployment → Logs

### Database (MongoDB):
- Go to Atlas Dashboard
- Click **Metrics** to see database usage
- Click **Browse Collections** to see stored predictions

---

## 💰 Cost Breakdown

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **MongoDB Atlas** | ✅ Yes | 512 MB storage, Shared cluster |
| **Render** | ✅ Yes | 750 hours/month, Sleeps after 15 min idle |
| **Vercel** | ✅ Yes | 100 GB bandwidth, Unlimited deployments |

**Total Cost: $0/month** with free tiers!

⚠️ **Note**: Render free tier spins down after inactivity. First request after idle takes ~30 seconds to wake up.

---

## 🎓 For Your BE Project Presentation

**Share these links**:
1. **Live App**: `https://your-project.vercel.app`
2. **GitHub Repo**: `https://github.com/YOUR_USERNAME/fraud-detection-system`
3. **Backend API Docs**: `https://your-api.onrender.com/docs` (FastAPI auto-generates this!)

**Demo Flow**:
1. Show the live website
2. Use "Suspicious Transaction" preset
3. Show high fraud detection
4. Explain the quantum-classical hybrid approach
5. Show GitHub code (emphasize your ML work in `src/`)

---

## 🆘 Need Help?

**Common Commands**:

```bash
# Check Git status
git status

# View deployment logs (Vercel)
vercel logs

# Test backend locally
cd backend
uvicorn main:app --reload

# Test frontend locally
cd frontend
npm run dev
```

**Resources**:
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com)

---

## ✅ Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created with password saved
- [ ] Network access configured (0.0.0.0/0)
- [ ] Connection string copied and tested
- [ ] Code pushed to GitHub
- [ ] Backend deployed to Render
- [ ] Environment variables added to Render
- [ ] Backend URL copied
- [ ] Frontend deployed to Vercel
- [ ] NEXT_PUBLIC_API_URL added to Vercel
- [ ] Live app tested and working
- [ ] Sample prediction successful

**Once all checked, you're LIVE! 🚀**
