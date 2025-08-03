# 🚀 EmergentTrader Render Deployment Guide

## 📋 Overview

This guide covers deploying EmergentTrader to Render with automated signal generation running 3 times daily.

### 🏗️ Architecture
- **Frontend**: Next.js 14 application
- **Backend**: Python FastAPI with SQLite database
- **Scheduled Jobs**: 3 cron jobs for signal generation (9 AM, 2 PM, 6 PM IST)
- **Database**: PostgreSQL on Render (production) or SQLite (development)

## 🔧 Pre-Deployment Setup

### 1. Environment Variables

Create these environment variables in Render:

#### Frontend Environment Variables
```bash
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://emergenttrader-backend.onrender.com
NEXT_PUBLIC_WS_URL=wss://emergenttrader-backend.onrender.com
NEXT_PUBLIC_APP_NAME=EmergentTrader
NEXT_PUBLIC_APP_VERSION=2.0.0
```

#### Backend Environment Variables
```bash
PYTHON_ENV=production
DATABASE_URL=postgresql://username:password@host:port/database
FRONTEND_URL=https://emergenttrader.onrender.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
NOTIFICATION_EMAIL=alerts@yourdomain.com
```

### 2. Database Setup

The deployment uses PostgreSQL for production. The database will be automatically created by Render.

## 🚀 Deployment Steps

### Step 1: Connect Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Select the `render-deployment` branch

### Step 2: Configure Services

The `render.yaml` file automatically configures:

#### Web Services
- **Frontend**: `emergenttrader-frontend`
  - Build: `npm install && npm run build`
  - Start: `npm start`
  - Port: 3000

- **Backend**: `emergenttrader-backend`
  - Build: `cd python_backend && pip install -r requirements_production.txt`
  - Start: `cd python_backend && python main_production.py`
  - Port: 8000

#### Cron Jobs
- **Morning Scan**: 9:00 AM IST (Monday-Friday)
- **Afternoon Scan**: 2:00 PM IST (Monday-Friday)  
- **Evening Scan**: 6:00 PM IST (Monday-Friday)

#### Database
- **PostgreSQL**: Automatically provisioned

### Step 3: Deploy
1. Click "Apply" to deploy all services
2. Wait for build and deployment to complete
3. Verify all services are running

## 📊 Automated Signal Generation

### Schedule Overview
```
🌅 Morning Scan (9:00 AM IST)
├── Strategies: multibagger, momentum, breakout
├── Min Confidence: 70%
├── Max Signals: 20
└── Email: Morning Trading Signals

☀️ Afternoon Scan (2:00 PM IST)
├── Strategies: swing_trading, mean_reversion, value_investing
├── Min Confidence: 75%
├── Max Signals: 15
└── Email: Afternoon Market Update

🌆 Evening Scan (6:00 PM IST)
├── Strategies: sector_rotation, low_volatility, fundamental_growth
├── Min Confidence: 80%
├── Max Signals: 10
└── Email: Evening Market Summary
```

### What Each Scan Does
1. **Generate Signals**: Runs multiple trading strategies
2. **ML Enhancement**: Applies machine learning predictions
3. **Filter & Rank**: Filters by confidence and ranks signals
4. **Save to Database**: Stores signals with metadata
5. **Track Progress**: Updates existing signal performance
6. **Send Notifications**: Emails and in-app notifications

## 🔍 Monitoring & Logs

### Health Checks
- **Frontend**: `https://emergenttrader.onrender.com/`
- **Backend**: `https://emergenttrader-backend.onrender.com/health`

### Log Access
```bash
# View backend logs
render logs emergenttrader-backend

# View cron job logs
render logs signal-generator-morning
render logs signal-generator-afternoon
render logs signal-generator-evening
```

### Monitoring Endpoints
- **Scheduled Status**: `/api/scheduled/status`
- **Signal Performance**: `/api/signals/performance`
- **Market Status**: `/api/market/status`

## 📧 Email Notifications

### Setup Gmail SMTP
1. Enable 2-factor authentication on Gmail
2. Generate an App Password
3. Use these settings:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   ```

### Email Templates
- **Morning**: 🌅 Morning Trading Signals
- **Afternoon**: ☀️ Afternoon Market Update  
- **Evening**: 🌆 Evening Market Summary
- **Errors**: 🚨 Error Alert

## 🛠️ Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Check build logs
render logs emergenttrader-backend --type=build

# Common fixes:
# - Update requirements_production.txt
# - Check Python version compatibility
# - Verify all imports are available
```

#### 2. Database Connection Issues
```bash
# Check database status
render services list

# Verify DATABASE_URL format:
# postgresql://username:password@host:port/database
```

#### 3. Cron Jobs Not Running
```bash
# Check cron job logs
render logs signal-generator-morning

# Verify cron schedule format (UTC time)
# 9 AM IST = 3:30 AM UTC
```

#### 4. Email Notifications Failing
```bash
# Check email configuration
# Verify Gmail App Password
# Check SMTP settings
```

### Debug Commands
```bash
# Test database connection
curl https://emergenttrader-backend.onrender.com/health

# Check scheduled job status
curl https://emergenttrader-backend.onrender.com/api/scheduled/status

# Test signal generation
curl -X POST https://emergenttrader-backend.onrender.com/api/signals/generate \
  -H "Content-Type: application/json" \
  -d '{"strategy": "multibagger", "limit": 5}'
```

## 📈 Performance Optimization

### Frontend Optimizations
- **Bundle Splitting**: Automatic code splitting
- **Image Optimization**: WebP/AVIF formats
- **Compression**: Gzip/Brotli compression
- **Caching**: Static asset caching

### Backend Optimizations
- **Connection Pooling**: Database connection pooling
- **Async Processing**: Background tasks
- **Caching**: Redis caching (optional)
- **Monitoring**: Health checks and metrics

## 🔒 Security

### Security Headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: origin-when-cross-origin
- Permissions-Policy: Restricted permissions

### Environment Security
- All secrets in environment variables
- No hardcoded credentials
- HTTPS enforcement
- CORS configuration

## 📊 Scaling

### Horizontal Scaling
```yaml
# In render.yaml, add:
services:
  - type: web
    name: emergenttrader-backend
    plan: standard  # Upgrade from starter
    numInstances: 2  # Multiple instances
```

### Database Scaling
```yaml
databases:
  - name: emergenttrader-db
    plan: standard  # Upgrade from starter
```

## 🔄 Updates & Maintenance

### Deployment Updates
1. Push changes to `render-deployment` branch
2. Render automatically rebuilds and deploys
3. Zero-downtime deployment

### Database Migrations
```python
# Add to scheduled job or run manually
python manage_database.py migrate
```

### Monitoring
- Set up alerts for failed cron jobs
- Monitor signal generation success rates
- Track application performance metrics

## 📞 Support

### Render Support
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)

### Application Support
- Check logs first: `render logs <service-name>`
- Review health check endpoints
- Monitor scheduled job reports

## 🎯 Success Metrics

After deployment, monitor:
- ✅ All 3 daily scans running successfully
- ✅ Signals being generated and saved
- ✅ Email notifications being sent
- ✅ Frontend accessible and responsive
- ✅ WebSocket connections working
- ✅ Database queries performing well

Your EmergentTrader application will now run fully automated on Render with professional-grade signal generation! 🚀
