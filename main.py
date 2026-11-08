import asyncio
import json
import os
from dotenv import load_dotenv
from upstash_redis.asyncio import Redis

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

async def fetch_dummy(id):
    await asyncio.sleep(0.5)
    return {"id": f"dummy:{id}", "value": 50000 + id * 1000}

async def main():
    redis = Redis(
        url=os.getenv("UPSTASH_REDIS_REST_URL"),
        token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
    )

    for i in range(10):
        await redis.delete(f"dummy:{i}")
    await redis.delete("counter")
    await redis.delete("permits_processed")

    dummies = await asyncio.gather(*(fetch_dummy(i) for i in range(10)))

    semaphore = asyncio.Semaphore(2)
    async def fetch_with_sem(id):
        async with semaphore:
            return await fetch_dummy(id)
    sem_results = await asyncio.gather(*(fetch_with_sem(i) for i in range(5)))

    results = []
    for d in dummies:
        key = d["id"]
        if await redis.exists(key):
            results.append({"id": key, "status": "skipped", "value": d["value"]})
        else:
            await redis.set(key, str(d["value"]), ex=86400)
            await redis.incr("counter")
            results.append({"id": key, "status": "new", "value": d["value"]})

    counter = await redis.get("counter")
    output = {
        "fetched": len(dummies),
        "semaphore_test": len(sem_results),
        "new": sum(1 for r in results if r["status"] == "new"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
        "counter": int(counter) if counter else 0,
        "results": results,
    }
    with open("output.json", "w") as f:
        json.dump(output, f, indent=2)

    check = await redis.get("dummy:0")
    return output, check

if __name__ == "__main__":
    output, check = asyncio.run(main())
    print(f"Done — Fetched {output['fetched']}, New {output['new']}, Counter {output['counter']}, Check dummy:0 = {check}")
    print("See output.json for full results")