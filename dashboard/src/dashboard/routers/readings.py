from typing import Annotated

from fastapi import APIRouter, Query

from ..dependencies import SettingsDep, StoreDep
from ..schemas import Reading, Thresholds

router = APIRouter(prefix="/api", tags=["readings"])


@router.get("/readings")
def list_readings(
    store: StoreDep,
    after_id: Annotated[int | None, Query(ge=0)] = None,
    limit: Annotated[int, Query(ge=1, le=5000)] = 300,
) -> list[Reading]:
    """Without `after_id`: the latest `limit` readings. With it: readings newer
    than that id, for polling. Always oldest first."""
    if after_id is None:
        return store.latest(limit)
    return store.after(after_id, limit)


@router.get("/thresholds")
def get_thresholds(settings: SettingsDep) -> Thresholds:
    return Thresholds(
        gas=settings.gas_threshold,
        temp_high=settings.temp_high_threshold,
        humidity_low=settings.humidity_low_threshold,
    )
