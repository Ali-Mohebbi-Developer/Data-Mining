import json
import re
from pathlib import Path
from typing import Any

import numpy as np

from src.config import FIGURES_DIR, INTERIM_DIR, MODELS_DIR, PROCESSED_DIR, RAW_DIR, REPORTS_DIR, TABLES_DIR


def ensure_directories() -> None:
    for path in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR, REPORTS_DIR, FIGURES_DIR, TABLES_DIR, MODELS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def normalize_whitespace(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def to_serializable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): to_serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_serializable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    return value


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_serializable(data), ensure_ascii=False, indent=2), encoding="utf-8")
