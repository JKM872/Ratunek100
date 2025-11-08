# ⚡ Performance Optimization Guide (PHASE 3)

## 🎯 Problem Solved
GitHub Actions scrapers risked exceeding 6-hour timeout with sequential processing of 600+ matches across 4 sports.

## ✅ Solution: Parallel Processing

### What Changed
1. **Parallel Workers: 5 → 8**
   - Now processes 8 matches simultaneously
   - Expected speedup: 5-8x faster
   - Sequential: ~3-4 hours → Parallel: ~30-45 minutes

2. **GitHub Actions Workflow Updated**
   - Added `--parallel` flag to all scraping commands
   - File: `.github/workflows/all-sports-scraping.yml`
   - Both email batches now use parallel mode

3. **Configuration**
   ```python
   MAX_PARALLEL_WORKERS = 8  # Was 5, now 8
   RETRY_ATTEMPTS = 3
   ODDS_FETCH_TIMEOUT = 15  # seconds
   TIMEOUT_MINUTES = 330  # 5.5 hours (safety margin)
   MAX_MEMORY_GB = 6.0  # Leave 1GB margin
   ```

## 🚀 Usage

### Local Testing
```bash
# Test with parallel mode
python scrape_and_notify.py \
  --date 2024-01-15 \
  --sports football volleyball basketball \
  --to your@email.com \
  --from-email your@email.com \
  --password "your-password" \
  --headless \
  --parallel

# Sequential mode (old way, slower)
python scrape_and_notify.py \
  --date 2024-01-15 \
  --sports football \
  --to your@email.com \
  --from-email your@email.com \
  --password "your-password" \
  --headless
```

### GitHub Actions
Workflows automatically use `--parallel` flag:
- `.github/workflows/all-sports-scraping.yml` - ✅ Updated
- Other workflows can be updated similarly

## 📊 Performance Metrics

### Expected Timing (8 workers)
| Matches | Sequential | Parallel (8x) | Speedup |
|---------|-----------|---------------|---------|
| 100     | 25 min    | 4 min         | 6.2x    |
| 300     | 75 min    | 12 min        | 6.2x    |
| 600     | 150 min   | 24 min        | 6.2x    |
| 1000    | 250 min   | 40 min        | 6.2x    |

### Real-World Factors
- Network latency: +10-20%
- API rate limiting: +5-10%
- Selenium overhead: +15-25%
- **Realistic speedup: 5-6x** (instead of 8x theoretical)

## 🔧 Technical Details

### Thread Pool Architecture
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process_url, url): url for url in urls}
    
    for future in as_completed(futures):
        result = future.result(timeout=60)
        # Process result
```

### Thread Safety
- ✅ Each thread has its own Selenium WebDriver
- ✅ Progress counter is thread-safe with `threading.Lock()`
- ✅ Results are collected safely with `as_completed()`
- ✅ No shared mutable state between threads

### Memory Management
- Monitor: `psutil` tracks RAM usage
- Limit: 6GB (GitHub Actions has 7GB)
- Cleanup: Garbage collector runs every 10 matches
- Restart: Driver restarts every 50 matches (memory leak prevention)

### Timeout Handling
- **Unix/Linux (GitHub Actions)**: Uses `signal.SIGALRM`
- **Windows**: Manual timeout check every 10 matches
- **Limit**: 330 minutes (5.5 hours) = 30-minute safety margin
- **Action**: Gracefully saves partial results on timeout

## ⚠️ Considerations

### When NOT to Use Parallel Mode
- 🚫 **Very small jobs** (<50 matches): Overhead not worth it
- 🚫 **Rate-limited APIs**: If API throttles requests
- 🚫 **Memory constrained**: <4GB RAM available
- 🚫 **Single CPU**: No parallel benefit

### When to Use Parallel Mode
- ✅ **Large jobs**: 200+ matches
- ✅ **GitHub Actions**: Always (has resources)
- ✅ **Fast networks**: Low latency environments
- ✅ **Time constraints**: Need results quickly

## 🐛 Troubleshooting

### "Too many open files" Error
**Cause**: OS file descriptor limit
**Solution**: Increase ulimit
```bash
ulimit -n 4096  # Increase to 4096 (default: 1024)
```

### High Memory Usage
**Symptom**: RAM > 6GB
**Solution**: Reduce workers
```python
MAX_PARALLEL_WORKERS = 5  # Down from 8
```

### Timeout Still Happening
**Symptom**: GitHub Actions timeout after 6h
**Solutions**:
1. Reduce `max_matches` per sport
2. Split into multiple workflows
3. Use `massive-scraping-parallel.yml` (3 batches)

### Inconsistent Results
**Cause**: Race conditions (rare)
**Solution**: Check for shared mutable state
- Verify each thread has own driver
- Check progress counter uses lock
- Review result collection

## 📈 Monitoring

### During Execution
```
🚀 TRYB RÓWNOLEGŁY: Przetwarzam 8 meczów jednocześnie...
   ⚡ To przyspieszy proces 5-8x!

[8/600] ✅ Team A vs Team B
[15/600] ✅ Team C vs Team D
...
📊 Status: Mecz 100/600 | Pamięć: 3.45GB | Czas: 12.5min
```

### After Completion
```
✅ Przetworzono 600 meczów równolegle!
   🎯 Kwalifikujących: 145
   ⏱️ Czas: 42 minuty
   💾 Pamięć peak: 4.2GB
```

## 🎓 Best Practices

1. **Always use parallel on GitHub Actions**
   - Resources available
   - Time is limited (6h)
   - No cost difference

2. **Test locally first**
   ```bash
   # Small test with parallel
   python scrape_and_notify.py --date today --sports football --max-matches 20 --parallel
   ```

3. **Monitor first runs**
   - Check logs for errors
   - Verify memory usage
   - Confirm timing improvements

4. **Adjust workers if needed**
   - 8 workers = aggressive (fastest)
   - 5 workers = balanced (safe)
   - 3 workers = conservative (slow)

## 🔮 Future Optimizations

### Potential Improvements
1. **Async/await** instead of threads (10-20% faster)
2. **Connection pooling** for API calls (reduce overhead)
3. **Caching** frequently accessed data (reduce API calls)
4. **Batch API requests** (if API supports it)
5. **Distributed scraping** (multiple GitHub runners)

### Not Recommended
- ❌ **More than 10 workers**: Diminishing returns, higher error rate
- ❌ **No timeout**: Could waste resources
- ❌ **No memory monitoring**: Risk of OOM kills
- ❌ **Shared WebDriver**: Race conditions

## 📚 Related Files

- `scrape_and_notify.py` - Main scraper with parallel mode
- `.github/workflows/all-sports-scraping.yml` - GitHub Actions workflow
- `.github/workflows/massive-scraping-parallel.yml` - 3-batch parallel mode
- `livesport_h2h_scraper.py` - Core scraping logic
- `livesport_odds_api_client.py` - Odds API client

## 🎉 Success Criteria

- ✅ GitHub Actions complete in <6 hours (target: <2 hours)
- ✅ Memory usage <6GB
- ✅ No timeout errors
- ✅ All matches processed successfully
- ✅ Speedup vs sequential: 5-6x minimum

## 📞 Support

If issues persist:
1. Check GitHub Actions logs
2. Review `outputs/*.csv` for partial results
3. Test locally with `--max-matches 50 --parallel`
4. Reduce `MAX_PARALLEL_WORKERS` if unstable
