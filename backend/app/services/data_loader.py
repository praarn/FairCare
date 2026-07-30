import json
from pathlib import Path
from functools import lru_cache

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache()
def load_treatments():
    # encoding="utf-8" is required here: these files contain Hindi
    # (Devanagari) text, and without an explicit encoding Python falls
    # back to the OS default — cp1252 on Windows — which cannot decode
    # multi-byte UTF-8 characters and raises UnicodeDecodeError.
    with open(DATA_DIR / "treatments.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache()
def load_cost_records():
    with open(DATA_DIR / "cost_records.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache()
def load_hospitals():
    with open(DATA_DIR / "hospitals.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache()
def load_schemes():
    with open(DATA_DIR / "schemes.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache()
def load_national_reference():
    with open(DATA_DIR / "national_reference.json", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_read_me", None)
    return data
