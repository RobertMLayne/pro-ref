import os
from pathlib import Path
from typing import Any, cast

import pytest
import vcr  # type: ignore[import]

CASSETTES = Path(__file__).resolve().parent / "cassettes"


def recorder(name: str) -> Any:
    """Return a VCR decorator that skips when cassette is unavailable."""

    cassette_path = CASSETTES / f"{name}.yaml"
    record_mode = os.getenv("VCR_MODE", "none")

    if record_mode == "none" and not cassette_path.exists():
        reason = (
            "Cassette '" + cassette_path.name + "' not found — set VCR_MODE to 'once'"
        )
        return pytest.mark.skip(reason=reason)

    record_mode_typed = cast(Any, record_mode)

    vcr_instance: Any = vcr.VCR(
        cassette_library_dir=str(CASSETTES),
        record_mode=record_mode_typed,
        filter_headers=[("X-API-KEY", "DUMMY")],
        match_on=["method", "scheme", "host", "port", "path", "query"],
    )

    decorator: Any = vcr_instance.use_cassette(str(cassette_path))
    return decorator
