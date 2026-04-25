"""Zombi İstilası için basit, ortam değişkeni kontrollü debug logger."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any


def _debug_aktif_mi() -> bool:
    return os.getenv("ZOMBI_DEBUG", "").strip() == "1"


def _zaman_damgasi() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _metinlestir(parcalar: tuple[Any, ...]) -> str:
    return " ".join(str(parca) for parca in parcalar)


def debug(*parcalar: Any) -> None:
    """Sadece ZOMBI_DEBUG=1 iken debug mesajı basar."""
    if _debug_aktif_mi():
        print(f"[DEBUG] {_zaman_damgasi()} {_metinlestir(parcalar)}")


def warn(*parcalar: Any) -> None:
    """Her zaman uyarı mesajı basar."""
    print(f"[WARN ] {_zaman_damgasi()} {_metinlestir(parcalar)}")


def error(*parcalar: Any) -> None:
    """Her zaman hata mesajı basar."""
    print(f"[ERROR] {_zaman_damgasi()} {_metinlestir(parcalar)}")
