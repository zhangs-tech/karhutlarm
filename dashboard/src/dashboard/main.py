import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import ReadingStore
from .routers import readings
from .subscriber import start_subscriber

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = ReadingStore(settings.db_path)
    client = start_subscriber(store, settings)
    app.state.store = store
    yield
    client.disconnect()
    client.loop_stop()
    store.close()


app = FastAPI(title="Karhutla Dashboard", lifespan=lifespan)
app.include_router(readings.router)

# Mounted last so it doesn't shadow the /api routes.
app.mount("/", StaticFiles(directory=settings.web_dir, html=True), name="web")
