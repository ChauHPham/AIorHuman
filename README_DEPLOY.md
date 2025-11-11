# 📦 Render Deployment - Complete Setup

## What Was Done

Your app is now configured to deploy on Render by hosting the model on Hugging Face Hub instead of including it in the repository.

### Changes Made:
1. ✅ Added `huggingface_hub` to `requirements.txt`
2. ✅ Created `src/model_loader.py` - Downloads model from Hugging Face if not found locally
3. ✅ Updated `src/inference.py` - Uses model loader automatically
4. ✅ Updated `app.py` - Reads `HF_MODEL_REPO` environment variable
5. ✅ Created `upload_model_to_hf.py` - Script to upload your model
6. ✅ Model already excluded from git (`.gitignore`)

---

## Quick Start (3 Steps)

### 1. Upload Model
```bash
pip install huggingface_hub
huggingface-cli login
python upload_model_to_hf.py --repo-id YOUR_USERNAME/ai-art-detector
```

### 2. Set Environment Variable in Render
- Go to Render Dashboard → Your Service → Environment
- Add: `HF_MODEL_REPO` = `YOUR_USERNAME/ai-art-detector`

### 3. Deploy
- Push to GitHub
- Render auto-deploys
- Model downloads automatically on first startup

---

## Detailed Guides

- **Quick Start**: See `QUICK_START_DEPLOY.md`
- **Step-by-Step**: See `DEPLOYMENT_STEPS.md`
- **Full Guide**: See `DEPLOY_RENDER.md`

---

## How It Works

```
Local Development:
  models/detector.pth exists? → Use it ✅
  models/detector.pth missing? → Download from HF ✅

Render Deployment:
  models/ excluded from git → Download from HF ✅
  Model cached on disk → Fast subsequent loads ✅
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_MODEL_REPO` | Yes | Your Hugging Face repo (e.g., `username/ai-art-detector`) |
| `HF_TOKEN` | Optional | Only needed for private repositories |
| `HF_MODEL_FILENAME` | Optional | Defaults to `detector.pth` |

---

## Testing Locally

Test the download functionality:

```bash
# Temporarily move model
mv models/detector.pth models/detector.pth.backup

# Set environment variable
export HF_MODEL_REPO=YOUR_USERNAME/ai-art-detector

# Run app - it will download model
python run_web.py
```

---

## Troubleshooting

**Model not downloading?**
- Check `HF_MODEL_REPO` is set correctly
- Verify repo exists and is accessible
- Check Render logs for errors

**Private repo?**
- Set `HF_TOKEN` environment variable
- Token needs read access

**Slow first request?**
- Normal! Model downloads on first request (~90MB)
- Subsequent requests use cache (fast)

---

## Files Reference

| File | Purpose |
|------|---------|
| `src/model_loader.py` | Downloads model from Hugging Face |
| `upload_model_to_hf.py` | Uploads model to Hugging Face |
| `DEPLOYMENT_STEPS.md` | Step-by-step deployment guide |
| `QUICK_START_DEPLOY.md` | Quick reference |
| `DEPLOY_RENDER.md` | Detailed deployment guide |

---

## Next Steps

1. ✅ Upload your model to Hugging Face (Step 1 above)
2. ✅ Configure Render environment variable (Step 2 above)
3. ✅ Deploy! (Step 3 above)

That's it! Your app should now deploy successfully. 🚀

