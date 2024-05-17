# pylint: disable=redefined-outer-name

import logging
from datetime import datetime
import asyncio
import uuid
import re
import redis.asyncio as redis
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
redis_client = redis.from_url("redis://redis", decode_responses=True)
keywords = ["checkpoint", "avanan", "email", "security"]


async def add_event(sentence: str):
    timestamp = datetime.now().timestamp()
    for keyword in keywords:
        occurrences = len(re.findall(rf"\b{keyword}\b", sentence, re.IGNORECASE))
        for _ in range(occurrences):
            event_id = str(uuid.uuid4())
            # logger.debug("Adding event: %s to keyword: %s", sentence, keyword)
            await redis_client.zadd(f"events:{keyword}", {event_id: timestamp})


async def get_stats(interval: int):
    cutoff = datetime.now().timestamp() - interval
    stats = {}
    tasks = []

    for keyword in keywords:
        task = asyncio.create_task(
            redis_client.zrangebyscore(f"events:{keyword}", cutoff, float("inf"))
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    for keyword, events in zip(keywords, results):
        # logger.debug("Keyword: %s, Events: %s", keyword, events)
        stats[keyword] = len(events)

    return stats


@app.post("/api/v1/events")
async def events(request: Request):
    try:
        sentence = (await request.body()).decode("utf-8")
        await add_event(sentence)
        return JSONResponse(content={"message": "Event added"}, status_code=201)
    except Exception as e:
        logger.error("Failed to add event: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to add event") from e


@app.get("/api/v1/stats")
async def stats(interval: int = Query(60)):
    try:
        result = await get_stats(interval)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error("Failed to get stats: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to get stats") from e
