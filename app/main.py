# pylint: disable=redefined-outer-name

import logging
from datetime import datetime
import asyncio
import uuid
import re
import redis.asyncio as redis
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from aiologger import Logger

logger = Logger.with_default_handlers(level=logging.INFO)

app = FastAPI()
redis_client = redis.from_url("redis://redis", decode_responses=True)
keywords = ["checkpoint", "avanan", "email", "security"]

keyword_patterns = {
    keyword: re.compile(rf"\b{keyword}\b", re.IGNORECASE) for keyword in keywords
}


async def add_event(sentence: str):
    timestamp = datetime.now().timestamp()
    tasks = []

    for keyword, pattern in keyword_patterns.items():
        occurrences = len(pattern.findall(sentence.lower()))
        if occurrences > 0:
            event_ids = {str(uuid.uuid4()): timestamp for _ in range(occurrences)}
            tasks.append(redis_client.zadd(f"events:{keyword}", event_ids))

    if tasks:
        await asyncio.gather(*tasks)


async def get_stats(interval: int):
    cutoff = datetime.now().timestamp() - interval
    tasks = [
        redis_client.zrangebyscore(f"events:{keyword}", cutoff, float("inf"))
        for keyword in keywords
    ]
    results = await asyncio.gather(*tasks)
    return {keyword: len(events) for keyword, events in zip(keywords, results)}


@app.post("/api/v1/events")
async def events(request: Request):
    try:
        sentence = (await request.body()).decode("utf-8")
        await add_event(sentence)
        return JSONResponse(content={"message": "Event added"}, status_code=201)
    except Exception as e:
        await logger.error("Failed to add event: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to add event") from e


@app.get("/api/v1/stats")
async def stats(interval: int = Query(60)):
    try:
        result = await get_stats(interval)
        return JSONResponse(content=result)
    except Exception as e:
        await logger.error("Failed to get stats: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to get stats") from e


@app.on_event("shutdown")
async def shutdown_event():
    await logger.shutdown()
