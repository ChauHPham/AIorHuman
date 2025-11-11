# 🚀 Render Deployment Steps - Complete Guide

## Overview
Your model file (90MB) is too large for Render's slug size. We'll host it on Hugging Face Hub and download it at runtime.

---

## ✅ Step 1: Upload Model to Hugging Face

### 1.1 Create Hugging Face Account
- Go to https://huggingface.co/
- Sign up (free)

### 1.2 Create Model Repository
- Visit: https://huggingface.co/new
- Select **"Model"**
- Repository name: `ai-art-detector` (or your choice)
- Visibility: **Public** (or Private if you prefer)
- Click **"Create repository"**

### 1.3 Install and Login
```bash
pip install huggingface_hub
huggingface-cli login
```
Enter your Hugging Face token (get it from https://huggingface.co/settings/tokens)

### 1.4 Upload Model
```bash
python upload_model_to_hf.py --repo-id YOUR_USERNAME/ai-art-detector
```

Replace `YOUR_USERNAME` with your actual Hugging Face username.

**Example:**
```bash
python upload_model_to_hf.py --repo-id johndoe/ai-art-detector
```

You should see:
```
✓ Successfully uploaded detector.pth to johndoe/ai-art-detector
  Model is now available at: https://huggingface.co/johndoe/ai-art-detector
```

---

## ✅ Step 2: Configure Render

### 2.1 Go to Render Dashboard
- Navigate to your service
- Click **"Environment"** tab

### 2.2 Add Environment Variable
Click **"Add Environment Variable"**:

| Key | Value |
|-----|-------|
| `HF_MODEL_REPO` | `YOUR_USERNAME/ai-art-detector` |

**Example:**
- Key: `HF_MODEL_REPO`
- Value: `johndoe/ai-art-detector`

### 2.3 (Optional) Private Repository
If you used a **private repository**, also add:

| Key | Value |
|-----|-------|
| `HF_TOKEN` | `hf_your_token_here` |

Get your token from: https://huggingface.co/settings/tokens

---

## ✅ Step 3: Verify Git Configuration

### 3.1 Check .gitignore
Make sure these lines exist in `.gitignore`:
```gitignore
models/
*.pth
```

They should already be there.

### 3.2 Verify Model is NOT Committed
```bash
git status
```

You should **NOT** see `models/detector.pth` in the output.

If it's already committed:
```bash
git rm --cached models/detector.pth
git commit -m "Remove model file from git"
```

---

## ✅ Step 4: Deploy to Render

### 4.1 Push to GitHub
```bash
git add .
git commit -m "Add Hugging Face model download support"
git push
```

### 4.2 Render Auto-Deploys
- Render will detect the push
- Build will start automatically
- On first startup, model downloads from Hugging Face (~90MB, one-time)
- Model is cached for subsequent requests

### 4.3 Monitor Deployment
- Check Render logs for:
  - `"Model downloaded from Hugging Face: ..."` (first time)
  - `"Model loaded from ..."` (success)

---

## ✅ Step 5: Test Your Deployment

1. Visit your Render URL
2. Try the quiz - it should work!
3. First request may be slow (downloading model)
4. Subsequent requests are fast (using cache)

---

## 🔧 How It Works

### Local Development
- App checks for `models/detector.pth` first
- If found → uses it (fast)
- If not found → downloads from Hugging Face

### Render Deployment
- Model not in repository (excluded by .gitignore)
- On startup → downloads from Hugging Face
- Cached to `~/.cache/huggingface/hub/`
- Subsequent deploys reuse cache

---

## 📋 Checklist

Before deploying, verify:

- [ ] Model uploaded to Hugging Face Hub
- [ ] Repository is accessible (test the URL)
- [ ] `HF_MODEL_REPO` environment variable set in Render
- [ ] `HF_TOKEN` set (if using private repo)
- [ ] `models/` folder excluded from git
- [ ] Code pushed to GitHub
- [ ] Render service connected to GitHub repo

---

## 🐛 Troubleshooting

### "Model not found" error
- ✅ Check `HF_MODEL_REPO` is set correctly
- ✅ Verify repo exists: https://huggingface.co/YOUR_USERNAME/ai-art-detector
- ✅ Check Render logs for download errors

### Slow first request
- ✅ Normal! Model downloads on first request (~90MB)
- ✅ Subsequent requests use cache (fast)

### Authentication errors
- ✅ Set `HF_TOKEN` environment variable
- ✅ Token must have read access to repository

### Build fails
- ✅ Check `huggingface_hub` is in `requirements.txt` (it is)
- ✅ Verify Python version in `render.yaml` matches your setup

---

## 📦 Files Changed

1. ✅ `requirements.txt` - Added `huggingface_hub`
2. ✅ `src/model_loader.py` - New file, handles model download
3. ✅ `src/inference.py` - Updated to use model loader
4. ✅ `app.py` - Updated to read `HF_MODEL_REPO` env var
5. ✅ `upload_model_to_hf.py` - New script to upload model

---

## 🎉 You're Done!

Your app should now deploy successfully on Render. The model will be downloaded automatically on first startup and cached for future use.

**Need help?** Check the detailed guide: `DEPLOY_RENDER.md`

