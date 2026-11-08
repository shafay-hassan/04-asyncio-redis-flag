# asyncio-redis-flag — Month 4
AsyncIO gather + Upstash Redis flag for dummy permits. Fetches concurrent with Semaphore, checks flag before SET, dedupes by key EXISTS.

Target: 10 dummy permits with gather + Semaphore + EXISTS — not real TDLR, test data for async + flag logic.

Features:

Fetches 10 dummies at once with gather, not one by one
Limits max 2 concurrent with Semaphore, not overload
Locks shared counter with Lock, not race condition
Waits for event with Event waiter/setter, not hard sleep
Sets flag with expire 1 day, not forever
Checks flag before SET to skip duplicate, not double insert
Counts permits with INCR, not Supabase COUNT
Checks time left with TTL and clears with DEL
Handles 10 fetched 10 new 0 skipped with gather 0.5 sec vs sequential 5.0 sec

Installation: pip install -r requirements.txt

Usage: python main.py

Output: Upstash texas-permits-flag — 10 flags SET, EXISTS 1, TTL 86400, Counter 10, Gather 0.5 sec

Stack: Python, AsyncIO, Upstash Redis Tokyo ap-northeast-1, upstash-redis

License: MIT