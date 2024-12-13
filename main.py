import asyncio

import pyodbc
from fastapi import FastAPI, HTTPException
import redis.asyncio as aioredis
import aiomysql
import aiohttp
import pika
import socket

app = FastAPI()

# Configuration for services
REDIS_URL = 'redis://localhost'
SQL_SERVER_HOST = 'localhost'
SQL_SERVER_PORT = 3306
EXTERNAL_API_URL = 'https://api.example.com/health'
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
SQL_SERVER_CONNECTION_STRING = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=.;DATABASE=TESTDB;UID=SA1;PWD=123'


async def check_redis():
    try:
        redis = aioredis.from_url(REDIS_URL)
        await redis.ping()
        await redis.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis check failed: {e}")


async def check_sql_server():
    try:
        conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"SQL Server check failed: {e}")


async def check_external_api():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EXTERNAL_API_URL) as response:
                if response.status != 200:
                    raise HTTPException(status_code=503, detail="External API check failed")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"External API check failed: {e}")


async def check_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT))
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RabbitMQ check failed: {e}")


async def check_network():
    try:
        socket.gethostbyname('www.google.com')
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Networking check failed: {e}")


@app.get("/health/liveness")
async def liveness():
    return {"status": "alive"}


@app.get("/health/readiness/redis")
async def readiness():
    await check_redis()


@app.get("/health/readiness/sql_server")
async def readiness():
    await check_sql_server()
    return {"status": "ready"}


@app.get("/health/readiness/external_api")
async def readiness():
    await check_external_api()
    return {"status": "ready"}


@app.get("/health/readiness/rabbitmq")
async def readiness():
    await check_rabbitmq()
    return {"status": "ready"}


@app.get("/health/readiness/network")
async def readiness():
    await check_network()
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
