# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import time
import pytest
import fakeredis.aioredis
from httpx import AsyncClient
from fastapi.testclient import TestClient
from .main import app


@pytest.fixture
def fake_redis_client():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def client(monkeypatch, fake_redis_client):
    monkeypatch.setattr("app.main.redis_client", fake_redis_client)
    return TestClient(app)


@pytest.fixture
async def fake_events(fake_redis_client):
    await fake_redis_client.zadd("events:email", {"event1": int(time.time())})
    await fake_redis_client.zadd("events:security", {"event2": int(time.time())})
    await fake_redis_client.zadd("events:checkpoint", {"event3": int(time.time())})
    await fake_redis_client.zadd("events:avanan", {"event4": int(time.time())})
    await fake_redis_client.zadd("events:avanan", {"event5": int(time.time())})
    await fake_redis_client.zadd("events:checkpoint", {"event6": int(time.time())})
    await fake_redis_client.zadd("events:checkpoint", {"event7": int(time.time())})


# pylint: disable=line-too-long
@pytest.mark.parametrize(
    "sentence, expected_keywords",
    [
        (
            "Avanan is a leading Enterprise Solution for Cloud Email and Collaboration Security",
            {"avanan": 1, "email": 1, "security": 1},
        ),
        (
            "CheckPoint Research have been observing an enormous rise in email attacks since the beginning of 2020",
            {"checkpoint": 1, "email": 1},
        ),
        (
            "Checkpoint and Avanan and email and Security and security",
            {"checkpoint": 1, "avanan": 1, "email": 1, "security": 2},
        ),
        (
            "Checkpoint CHECKPOINT CheckPoinT CHECKPOINTS",
            {"checkpoint": 3},
        ),
        (
            "email EMAIL- eMaIl, emaail - emaaail - email -emails",
            {"email": 4},
        ),
        ("", {}),
    ],
)
@pytest.mark.asyncio
async def test_add_event(client, fake_redis_client, sentence, expected_keywords):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/events", data=sentence.encode("utf-8"))
    assert response.status_code == 201
    assert response.json() == {"message": "Event added"}

    for keyword, expected_count in expected_keywords.items():
        events = await fake_redis_client.zrange(f"events:{keyword}", 0, -1)
        assert (
            len(events) == expected_count
        ), f"Expected {expected_count} events for keyword '{keyword}', but got {len(events)}"


@pytest.mark.asyncio
async def test_get_stats(client, fake_redis_client, fake_events):
    await fake_events

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/stats?interval=60")
    stats = response.json()

    assert response.status_code == 200
    assert stats["email"] == 1
    assert stats["security"] == 1
    assert stats["checkpoint"] == 3
    assert stats["avanan"] == 2


@pytest.mark.asyncio
async def test_get_stats_no_events(client):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/stats?interval=60")
    stats = response.json()

    assert response.status_code == 200
    assert stats["email"] == 0
    assert stats["security"] == 0
    assert stats["checkpoint"] == 0
    assert stats["avanan"] == 0
