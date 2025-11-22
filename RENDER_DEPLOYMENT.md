# Render Deployment Guide

## 🚀 **Quick Deploy to Render**

### **Step 1: Prepare Your Repository**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

### **Step 2: Deploy to Render**

1. **Go to Render Dashboard:**
   - Visit: https://render.com
   - Sign up/Login with GitHub

2. **Create New Blueprint:**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository containing your auth service
   - Render will detect the `render.yaml` file

3. **Review Services:**
   - ✅ **Web Service:** billfusion-auth-service
   - ✅ **PostgreSQL:** billfusion-auth-db
   - ✅ **Redis:** billfusion-auth-redis

4. **Click "Apply"**

### **Step 3: Configure Environment Variables**

In Render Dashboard → Your Service → Environment:

#### **Required Secrets:**
```bash
# Security (Generate strong random strings)
SECRET_KEY=your-super-secret-32-char-key-here
JWT_SECRET_KEY=your-jwt-secret-32-char-key-here

# Email (Gmail App Password)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# Google OAuth (From Google Console)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Frontend URL (Update after frontend deployment)
FRONTEND_URL=https://your-frontend-domain.vercel.app
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]

# Optional: Monitoring
SENTRY_DSN=your-sentry-dsn-for-error-tracking
```

#### **Auto-Generated (by Render):**
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `PORT` - Application port

### **Step 4: Wait for Deployment**

- ⏳ **Database:** ~2-3 minutes
- ⏳ **Redis:** ~1-2 minutes  
- ⏳ **Web Service:** ~5-10 minutes

### **Step 5: Test Your Deployment**

Your service will be available at:
```
https://billfusion-auth-service.onrender.com
```

**Test endpoints:**
- Health: `https://billfusion-auth-service.onrender.com/health`
- API Docs: `https://billfusion-auth-service.onrender.com/docs` (if DEBUG=true)
- Register: `POST https://billfusion-auth-service.onrender.com/api/v1/auth/register`

---

## 📋 **Configuration Files Created**

| File | Purpose |
|------|----------|
| `render.yaml` | Render Blueprint (defines all services) |
| `Dockerfile.render` | Production Docker configuration |
| `.env.production` | Production environment template |
| `start.sh` | Production startup script |

---

## 🔧 **Production Features Enabled**

### **Security:**
- ✅ Strong secret key validation
- ✅ HTTPS-only CORS origins
- ✅ Security headers middleware
- ✅ Trusted host middleware
- ✅ Rate limiting

### **Performance:**
- ✅ Database connection pooling
- ✅ Redis connection pooling
- ✅ GZip compression
- ✅ Optimized logging

### **Monitoring:**
- ✅ Health check endpoints
- ✅ Prometheus metrics
- ✅ Structured JSON logging
- ✅ Sentry error tracking (optional)

### **Reliability:**
- ✅ Graceful startup/shutdown
- ✅ Database migration on startup
- ✅ Connection retry logic
- ✅ Global exception handling

---

## 🎯 **Post-Deployment Setup**

### **1. Create Admin User**

The startup script automatically creates admin@billfusion.com with default password: Admin123!

**Change this immediately after first login!**

### **2. Update Frontend Configuration**

Update your frontend's API base URL:

```javascript
// frontend/src/config/env.js
const config = {
  API_BASE_URL: 'https://billfusion-auth-service.onrender.com/api/v1'
};
```

### **3. Configure Custom Domain (Optional)**

In Render Dashboard:
1. Go to your service → Settings
2. Add custom domain: `api.billfusion.com`
3. Update DNS records as instructed

---

## 🔐 **Security Checklist**

### **Before Going Live:**

- [ ] **Change default admin password**
- [ ] **Set strong SECRET_KEY (32+ chars)**
- [ ] **Set strong JWT_SECRET_KEY (32+ chars)**
- [ ] **Configure real SMTP credentials**
- [ ] **Set up Google OAuth properly**
- [ ] **Update CORS_ORIGINS with real frontend domain**
- [ ] **Enable Sentry for error tracking**
- [ ] **Test all authentication flows**
- [ ] **Verify rate limiting works**
- [ ] **Check security headers**

---

## 📊 **Monitoring & Logs**

### **View Logs:**
```bash
# In Render Dashboard
Service → Logs → Live Logs
```

### **Metrics:**
```bash
# Prometheus metrics
https://billfusion-auth-service.onrender.com/metrics
```

### **Health Checks:**
```bash
# Basic health
curl https://billfusion-auth-service.onrender.com/health

# Detailed readiness
curl https://billfusion-auth-service.onrender.com/ready
```

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**1. Service won't start:**
- Check environment variables are set
- Verify DATABASE_URL and REDIS_URL
- Check logs for specific errors

**2. Database connection failed:**
- Ensure PostgreSQL service is running
- Check DATABASE_URL format
- Verify network connectivity

**3. CORS errors:**
- Update CORS_ORIGINS with correct frontend domain
- Ensure HTTPS is used in production

**4. Authentication not working:**
- Verify JWT_SECRET_KEY is set
- Check token expiration settings
- Ensure database migrations ran

---

## 💰 **Pricing**

### **Free Tier (Starter Plan):**
- ✅ Web Service: 512MB RAM, sleeps after 15min inactivity
- ✅ PostgreSQL: 1GB storage, 97 connection limit
- ✅ Redis: 25MB storage
- ✅ Custom domains
- ✅ SSL certificates

### **Paid Tier (Standard Plan - $7/month):**
- ✅ Web Service: Always on, 1GB RAM
- ✅ PostgreSQL: 10GB storage
- ✅ Redis: 1GB storage
- ✅ Better performance
- ✅ Priority support

---

## 🔄 **Updates & Maintenance**

### **Deploy Updates:**
```bash
# Push to GitHub
git add .
git commit -m "Update auth service"
git push origin main

# Render auto-deploys from main branch
```

### **Manual Deploy:**
- Render Dashboard → Service → Manual Deploy

### **Database Migrations:**
- Automatic on startup via `start.sh`
- Manual: Use Render console to run `alembic upgrade head`

---

**🎉 Your auth service is now production-ready on Render!**

**Service URL:** `https://billfusion-auth-service.onrender.com`

---

## ⚠️ **Important Note About Redis**

Render's free tier doesn't include Redis in blueprints. You have two options:

### **Option 1: Use Railway Instead (Recommended)**
Railway includes Redis in the free tier! See `RAILWAY_DEPLOYMENT.md` for details.

### **Option 2: Use External Redis**
- **Upstash** (free tier: 10,000 commands/day) - https://upstash.com
- **Redis Cloud** (free tier: 30MB) - https://redis.com/try-free

Then set `REDIS_URL` manually in Render environment variables.
