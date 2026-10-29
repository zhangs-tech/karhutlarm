from typing import Annotated

from fastapi import Depends, Request

from .config import Settings, get_settings
from .db import ReadingStore


def get_store(request: Request) -> ReadingStore:
    return request.app.state.store


StoreDep = Annotated[ReadingStore, Depends(get_store)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
