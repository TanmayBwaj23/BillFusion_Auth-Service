# Railway Deployment Guide

## 🚀 **Why Railway?**

Railway is better than Render for your auth service because:
- ✅ **Built-in Redis support** (free tier includes Redis!)
- ✅ **PostgreSQL included** (free tier: 512MB RAM, 1GB storage)
- ✅ **$5 free credit/month** (no credit card required)
- ✅ **Faster deployments** (~2-3 minutes)
- ✅ **Better developer experience**
- ✅ **Automatic HTTPS**
- ✅ **Built-in metrics and logs**

---

## 🎯 **Quick Deploy to Railway**

### **Step 1: Prepare Your Repository**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Railway deployment configuration"
   git push origin main
   ```

### **Step 2: Deploy to Railway**

#### **Option A: Deploy via Railway Dashboard (Recommended)**

1. **Go to Railway:**
   - Visit: https://railway.app
   - Sign up/Login with GitHub (no credit card required!)

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect it's a Python app

3. **Add PostgreSQL:**
   - In your project, click "New"
   - Select "Database" → "Add PostgreSQL"
   - Railway automatically creates `DATABASE_URL` variable

4. **Add Redis:**
   - Click "New" again
   - Select "Database" → "Add Redis"
   - Railway automatically creates `REDIS_URL` variable

5. **Configure Environment Variables:**
   Click on your web service → Variables → Add these:

   ```bash
   # Security (Generate strong 32+ character secrets)
   SECRET_KEY=your-super-secret-32-char-key-here
   JWT_SECRET_KEY=your-jwt-secret-32-char-key-here
   
   # Email (Gmail App Password)
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-gmail-app-password
   
   # Google OAuth
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   
   # Frontend URL (Update after frontend deployment)
   FRONTEND_URL=https://your-frontend-domain.vercel.app
   CORS_ORIGINS=["https://your-frontend-domain.vercel.app","https://billfusion.com"]
   
   # Application
   ENVIRONMENT=production
   DEBUG=false
   APP_NAME=BillFusion Auth Service
   APP_VERSION=1.0.0
   
   # Email Config
   EMAIL_BACKEND=smtp
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USE_TLS=true
   FROM_EMAIL=noreply@billfusion.com
   FROM_NAME=BillFusion
   
   # Optional: Monitoring
   SENTRY_DSN=your-sentry-dsn
   ```

6. **Deploy:**
   - Railway automatically deploys on push to main
   - First deployment takes ~3-5 minutes

#### **Option B: Deploy via Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd auth-service
railway init

# Link to project
railway link

# Add PostgreSQL
railway add --database postgresql

# Add Redis
railway add --database redis

# Set environment variables
railway variables set SECRET_KEY=your-secret-key
railway variables set JWT_SECRET_KEY=your-jwt-secret

# Deploy
railway up
```

---

## 🔗 **Your Service URLs**

After deployment, Railway provides:
- **Web Service:** `https://your-app.up.railway.app`
- **Custom Domain:** Configure in Settings → Domains

---

## 📋 **Configuration Files Created**

| File | Purpose |
|------|---------|
| `railway.json` | Railway service configuration (JSON format) |
| `railway.toml` | Railway service configuration (TOML format) |
| `RAILWAY_DEPLOYMENT.md` | This deployment guide |

---

## 🎯 **Post-Deployment Setup**

### **1. Run Database Migrations**

Railway doesn't auto-run migrations, so you need to do it once:

**Option A: Via Railway CLI:**
```bash
railway run alembic upgrade head
```

**Option B: Via Railway Dashboard:**
1. Go to your service → Settings
2. Add to "Deploy Command": `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### **2. Create Admin User**

**Via Railway CLI:**
```bash
railway run python -c "
import asyncio
from app.core.database import get_db_session
from app.services.auth_service import AuthService
from app.models.user import User
from sqlalchemy import select

async def create_admin():
    async with get_db_session() as db:
        auth_service = AuthService(db)
        stmt = select(User).where(User.email == 'admin@billfusion.com')
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = await auth_service.register_user(
                email='admin@billfusion.com',
                password='Admin123!',
                first_name='System',
                last_name='Administrator',
                role='ADMIN'
            )
            admin.status = 'ACTIVE'
            admin.is_email_verified = True
            await db.commit()
            print('Admin user created!')

asyncio.run(create_admin())
"
```

### **3. Update Frontend Configuration**

```javascript
// frontend/src/config/env.js
const config = {
  API_BASE_URL: 'https://your-app.up.railway.app/api/v1'
};
```

### **4. Configure Custom Domain (Optional)**

1. Go to your service → Settings → Domains
2. Click "Add Domain"
3. Enter: `api.billfusion.com`
4. Update your DNS with the provided CNAME record
5. Railway automatically provisions SSL certificate

---

## 🔧 **Railway Features**

### **Built-in Services:**
- ✅ PostgreSQL (512MB RAM, 1GB storage)
- ✅ Redis (25MB storage)
- ✅ Automatic backups
- ✅ Connection pooling

### **Monitoring:**
- ✅ Real-time logs
- ✅ Metrics dashboard (CPU, Memory, Network)
- ✅ Deployment history
- ✅ Health checks

### **Developer Experience:**
- ✅ Auto-deploy on git push
- ✅ Preview deployments for PRs
- ✅ Rollback to any deployment
- ✅ Environment variables management
- ✅ CLI for local development

---

## 📊 **Monitoring & Logs**

### **View Logs:**
```bash
# Via CLI
railway logs

# Via Dashboard
Project → Service → Logs (real-time)
```

### **View Metrics:**
- Dashboard → Service → Metrics
- CPU, Memory, Network usage
- Request rate and response times

### **Health Checks:**
```bash
# Test health endpoint
curl https://your-app.up.railway.app/health

# Test readiness
curl https://your-app.up.railway.app/ready
```

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
- [ ] **Verify database backups are enabled**
- [ ] **Set up custom domain with SSL**

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**1. Service won't start:**
```bash
# Check logs
railway logs

# Common fixes:
- Verify all environment variables are set
- Check DATABASE_URL and REDIS_URL are auto-generated
- Ensure requirements.txt is complete
```

**2. Database connection failed:**
```bash
# Verify PostgreSQL is running
railway status

# Check connection string
railway variables get DATABASE_URL
```

**3. Redis connection failed:**
```bash
# Verify Redis is running
railway status

# Check connection string
railway variables get REDIS_URL
```

**4. Migrations not running:**
```bash
# Run manually
railway run alembic upgrade head

# Or update deploy command
railway service update --deploy-command "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
```

**5. CORS errors:**
- Update CORS_ORIGINS in environment variables
- Ensure frontend domain is included
- Redeploy after changes

---

## 💰 **Pricing**

### **Free Tier (Hobby Plan):**
- ✅ **$5 credit/month** (no credit card required)
- ✅ **512MB RAM** per service
- ✅ **1GB storage** for PostgreSQL
- ✅ **25MB storage** for Redis
- ✅ **Unlimited projects**
- ✅ **Custom domains**
- ✅ **Automatic SSL**
- ✅ **Perfect for development and small production apps**

### **Usage Estimate:**
- Web Service: ~$2-3/month
- PostgreSQL: ~$1/month
- Redis: ~$0.50/month
- **Total: ~$3.50-4.50/month** (covered by free $5 credit!)

### **Paid Tier (Developer Plan - $5/month):**
- ✅ **$5 credit + $5 included usage** = $10 total
- ✅ **8GB RAM** per service
- ✅ **Priority support**
- ✅ **Team collaboration**

---

## 🔄 **Updates & Maintenance**

### **Automatic Deployments:**
```bash
# Push to GitHub
git add .
git commit -m "Update auth service"
git push origin main

# Railway auto-deploys from main branch
```

### **Manual Deployment:**
```bash
# Via CLI
railway up

# Via Dashboard
Project → Service → Deploy → Redeploy
```

### **Rollback:**
```bash
# Via CLI
railway rollback

# Via Dashboard
Project → Service → Deployments → Select previous → Rollback
```

### **Database Backups:**
- Automatic daily backups (retained for 7 days)
- Manual backup: Dashboard → PostgreSQL → Backups → Create Backup

---

## 🎉 **Comparison: Railway vs Render**

| Feature | Railway | Render |
|---------|---------|--------|
| **Redis Support** | ✅ Built-in | ❌ Manual setup required |
| **Free Tier** | $5 credit/month | 512MB RAM, sleeps after 15min |
| **PostgreSQL** | ✅ Included | ✅ Included |
| **Deployment Speed** | ~2-3 minutes | ~5-10 minutes |
| **CLI** | ✅ Excellent | ✅ Good |
| **Metrics** | ✅ Built-in | ✅ Built-in |
| **Custom Domains** | ✅ Free | ✅ Free |
| **Auto-deploy** | ✅ Yes | ✅ Yes |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Winner: Railway** (for your use case with Redis requirement)

---

## 📚 **Next Steps**

1. **Deploy to Railway** using this guide
2. **Run database migrations**
3. **Create admin user**
4. **Test all endpoints**
5. **Update frontend API URL**
6. **Deploy frontend to Vercel**
7. **Configure custom domain**

---

## 🔗 **Useful Links**

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app
- **Railway CLI:** https://docs.railway.app/develop/cli
- **Railway Status:** https://status.railway.app
- **Railway Discord:** https://discord.gg/railway

---

**🎉 Your auth service is now production-ready on Railway!**

**Service URL:** `https://your-app.up.railway.app`

**With Railway, you get PostgreSQL + Redis + Web Service all in one platform with $5 free credit/month!**
