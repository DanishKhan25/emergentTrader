-- PyCharm SQLite Queries for EmergentTrader Database
-- Copy these queries into PyCharm's SQL Console

-- 1. View all active signals
SELECT 
    signal_id,
    symbol,
    strategy,
    signal_type,
    confidence,
    price,
    generated_at,
    status
FROM signals 
WHERE status = 'ACTIVE'
ORDER BY generated_at DESC;

-- 2. Count signals by strategy
SELECT 
    strategy,
    COUNT(*) as signal_count,
    AVG(confidence) as avg_confidence
FROM signals 
GROUP BY strategy
ORDER BY signal_count DESC;

-- 3. View recent signals (last 7 days)
SELECT 
    symbol,
    strategy,
    signal_type,
    confidence,
    generated_at
FROM signals 
WHERE generated_at >= datetime('now', '-7 days')
ORDER BY generated_at DESC;

-- 4. Check database schema
SELECT name, sql 
FROM sqlite_master 
WHERE type='table';

-- 5. View consensus signals
SELECT 
    consensus_id,
    symbol,
    signal_type,
    strategies,
    strategy_count,
    consensus_strength,
    generated_at
FROM consensus_signals
WHERE status = 'ACTIVE'
ORDER BY consensus_strength DESC;

-- 6. Strategy performance summary
SELECT 
    strategy,
    COUNT(*) as total_signals,
    COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_signals,
    AVG(confidence) as avg_confidence,
    MIN(generated_at) as first_signal,
    MAX(generated_at) as latest_signal
FROM signals
GROUP BY strategy;

-- 7. Daily signal generation stats
SELECT 
    DATE(generated_at) as date,
    COUNT(*) as signals_generated,
    COUNT(DISTINCT strategy) as strategies_used,
    COUNT(DISTINCT symbol) as unique_symbols
FROM signals
GROUP BY DATE(generated_at)
ORDER BY date DESC;

-- 8. Top performing symbols (by signal count)
SELECT 
    symbol,
    COUNT(*) as signal_count,
    COUNT(DISTINCT strategy) as strategies_count,
    GROUP_CONCAT(DISTINCT strategy) as strategies_used
FROM signals
GROUP BY symbol
HAVING signal_count > 1
ORDER BY signal_count DESC;
