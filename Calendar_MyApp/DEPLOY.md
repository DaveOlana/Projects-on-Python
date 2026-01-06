# CalendME - Render Deployment Guide

## Quick Deploy to Render

### 1. Prepare Your Repository

Make sure you have:
- ✅ `requirements.txt` (includes gunicorn)
- ✅ `Procfile` (tells Render how to start the app)
- ✅ All code committed to Git

### 2. Deploy on Render

1. **Go to [render.com](https://render.com)** and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub/GitLab repository
4. Configure:
   - **Name:** `calendme` (or your choice)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free tier works fine

5. Click **"Create Web Service"**
6. Wait 2-3 minutes for deployment
7. Your app will be live at: `https://calendme.onrender.com`

### 3. Environment Settings (Optional)

In Render dashboard, you can add:
- **FLASK_ENV:** `production`
- **DEBUG:** `False`

### 4. Important Notes

✅ **File Storage:** Render's free tier has persistent disk storage - your temp/permanent folders will work!
✅ **Auto-deploys:** Pushes to your repo auto-deploy
✅ **HTTPS:** Render provides free SSL certificates
✅ **WebCal URLs:** Will use your Render domain automatically

### 5. Testing After Deployment

1. Visit your Render URL
2. Add some events
3. Test WebCal export (button should show "Add to Calendar")
4. Test Download .ics
5. Check Import Guide modal

---

## Alternative: Local Testing with Gunicorn

Before deploying, test locally:

```bash
pip install -r requirements.txt
gunicorn app:app
```

Access at `http://127.0.0.1:8000`

---

**That's it! Your CalendME app is now production-ready! 🚀**
