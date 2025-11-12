# Quick Fix: Quiz Loader Not Initialized

## The Problem
You're seeing: "Quiz dataset not available. Quiz loader not initialized."

This means the quiz loader didn't initialize on startup.

## Quick Fix Steps

### Step 1: Check Environment Variable
In Render Dashboard → Your Service → Environment, verify:
- **Key:** `HF_QUIZ_IMAGES_REPO`
- **Value:** `your-username/ai-art-quiz-images` (your actual repo)

**Important:** No spaces, no quotes, exact format: `username/repo-name`

### Step 2: Check Health Endpoint
After deploying, visit: `https://your-app.onrender.com/health`

You should see:
```json
{
  "quiz_loader_status": "loaded",
  "quiz_loader_count": 100,
  "hf_quiz_repo": "your-username/ai-art-quiz-images",
  "quiz_loader_initialized": true
}
```

If you see:
- `"quiz_loader_initialized": false` → Quiz loader didn't initialize
- `"hf_quiz_repo": "Not set"` → Environment variable not set
- `"quiz_loader_count": 0` → Images didn't load

### Step 3: Check Render Logs
Look for these messages in Render logs:

**Success:**
```
✓ Quiz dataset loaded: 100 images from Hugging Face Hub
```

**Failure:**
```
Warning: Could not load quiz dataset: ...
```

### Step 4: Verify Repository
1. Go to: https://huggingface.co/your-username/ai-art-quiz-images
2. Check that:
   - Repository exists
   - `manifest.json` file exists
   - `AI/` and `Human/` folders exist
   - Repository is public (or you have `HF_TOKEN` set)

### Step 5: Re-upload if Needed
If repository is missing files:

```bash
# Login
huggingface-cli login

# Re-upload
python upload_quiz_images_to_hf.py --repo-id your-username/ai-art-quiz-images
```

## Common Issues

### Issue 1: Environment Variable Not Set
**Symptom:** `"hf_quiz_repo": "Not set"` in health endpoint

**Fix:** Add `HF_QUIZ_IMAGES_REPO` in Render environment variables

### Issue 2: Wrong Repository Name
**Symptom:** 404 errors in logs

**Fix:** Double-check the repository name matches exactly

### Issue 3: Repository Not Public
**Symptom:** 401 Unauthorized errors

**Fix:** Either make repo public OR set `HF_TOKEN` environment variable

### Issue 4: Manifest Missing
**Symptom:** "Could not load from Hugging Face Hub"

**Fix:** Re-upload images using `upload_quiz_images_to_hf.py`

## What Changed

I've updated the code to:
1. ✅ Initialize quiz loader on app startup (works with gunicorn)
2. ✅ Add detailed logging to see what's happening
3. ✅ Add health endpoint to check status
4. ✅ Better error messages

## Next Steps

1. **Commit and push** the updated code
2. **Redeploy** on Render
3. **Check health endpoint**: `https://your-app.onrender.com/health`
4. **Check logs** for initialization messages
5. **Test quiz** - it should work now!

## Still Not Working?

Share:
1. What you see in `/health` endpoint
2. Error messages from Render logs
3. Your `HF_QUIZ_IMAGES_REPO` value (without sensitive info)

And I'll help debug further!

