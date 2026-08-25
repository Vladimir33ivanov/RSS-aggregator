from fastapi import FastAPI

from app.api.routes import feed, health, sources

app = FastAPI(title="RSS Aggregator", version="2.0.0-alpha.1")

app.include_router(health.router)
app.include_router(sources.router)
app.include_router(feed.router)
