# Memory Fix for Render Deployment

## Issues Identified

1. **PyTorch with CUDA**: Installing full CUDA PyTorch (~2GB+) on CPU-only Render servers
2. **Too many workers**: 4 workers in Dockerfile, 2 in render.yaml - each loads model separately (4x memory!)
3. **Model loaded on startup**: Each worker process loads model immediately

## Fixes Applied

### 1. CPU-Only PyTorch
- Created `requirements-cpu.txt` (without PyTorch)
- Updated `render.yaml` to install CPU-only PyTorch first
- Saves ~2GB+ of memory

### 2. Reduced Workers
- Changed from 4 workers → **1 worker** (Dockerfile)
- Changed from 2 workers → **1 worker** (render.yaml)
- Added `--threads 2` for concurrent requests within single worker
- Each worker loads model separately, so 1 worker = 1x memory instead of 4x

### 3. Increased Timeout
- Changed timeout from 120s → **300s**
- Allows time for model download on first request

## Memory Savings

| Before | After | Savings |
|--------|-------|---------|
| PyTorch CUDA: ~2GB | PyTorch CPU: ~500MB | **~1.5GB** |
| 4 workers × model: ~360MB | 1 worker × model: ~90MB | **~270MB** |
| **Total** | | **~1.77GB saved** |

## Files Changed

1. ✅ `requirements-cpu.txt` - New file, CPU-only dependencies
2. ✅ `render.yaml` - Install CPU PyTorch, 1 worker, longer timeout
3. ✅ `Dockerfile` - 1 worker, longer timeout, use requirements-cpu.txt

## Next Steps

1. **Commit changes:**
   ```bash
   git add requirements-cpu.txt render.yaml Dockerfile
   git commit -m "Fix memory issues: use CPU-only PyTorch and reduce workers"
   git push
   ```

2. **Redeploy on Render** - should work now!

3. **Monitor**: Check Render logs to confirm it starts without memory errors

## Why This Works

- **CPU-only PyTorch**: No CUDA libraries = much smaller install
- **1 worker**: Only one copy of model in memory
- **Threads**: Still handles concurrent requests (2 threads per worker)
- **Longer timeout**: Allows model download time on first request

## Expected Results

- ✅ Build completes without memory issues
- ✅ App starts successfully
- ✅ Model downloads from Hugging Face on first request
- ✅ Subsequent requests are fast (model cached)

