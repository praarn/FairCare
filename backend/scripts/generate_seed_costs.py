"""Deterministically (re)generate ``app/data/seed/cost_records.json``.

This is a developer tool, not part of the running app. It expands a compact
base-rate table into per-city / per-hospital-type sample rows using published
cost-of-living-style multipliers and a seeded jitter, so the seed set is
realistic *and* reproducible (run it again, get byte-identical output).

Every row's ``source`` says plainly that it is model-derived SAMPLE DATA — it
is not a scrape of real invoices. Replace with sourced CGHS / PM-JAY / state
tariff data before any real use.

    python -m scripts.generate_seed_costs
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SEED_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "seed"

# City -> (state, relative cost level vs Delhi=1.00)
CITIES = {
    "Delhi": ("Delhi", 1.00),
    "Mumbai": ("Maharashtra", 1.15),
    "Bengaluru": ("Karnataka", 1.05),
    "Pune": ("Maharashtra", 0.95),
    "Chennai": ("Tamil Nadu", 0.95),
    "Hyderabad": ("Telangana", 0.90),
    "Kolkata": ("West Bengal", 0.85),
}

# hospital_type -> multiplier vs a government-hospital baseline
TYPE_MULT = {
    "govt": 1.0,
    "private_low": 2.3,
    "private_mid": 3.6,
    "private_high": 5.0,
}

# treatment_id -> (govt baseline avg INR, [hospital types to emit], [cities to emit])
ALL = list(CITIES)
CORE = ["Delhi", "Mumbai", "Bengaluru", "Chennai"]
SURGERY_TYPES = ["govt", "private_low", "private_mid", "private_high"]
COMMON_TYPES = ["govt", "private_low", "private_mid"]
PRIVATE_ONLY = ["private_low", "private_mid", "private_high"]

BASE = {
    "t_appendectomy": (14000, COMMON_TYPES, ALL),
    "t_normal_delivery": (3000, COMMON_TYPES, ALL),
    "t_c_section": (12000, COMMON_TYPES, ALL),
    "t_cataract": (6000, COMMON_TYPES, ALL),
    "t_knee_replacement": (105000, SURGERY_TYPES, ALL),
    "t_dialysis": (1200, COMMON_TYPES, ALL),
    "t_hernia_repair": (16000, COMMON_TYPES, ALL),
    "t_gallbladder_removal": (22000, COMMON_TYPES, ALL),
    "t_tonsillectomy": (12000, COMMON_TYPES, CORE),
    "t_hysterectomy": (28000, COMMON_TYPES, ALL),
    "t_angioplasty": (120000, SURGERY_TYPES, ALL),
    "t_bypass_surgery": (175000, SURGERY_TYPES, CORE + ["Hyderabad"]),
    "t_hip_replacement": (115000, SURGERY_TYPES, CORE + ["Pune"]),
    "t_fracture_fixation": (35000, COMMON_TYPES, ALL),
    "t_kidney_stone_removal": (30000, COMMON_TYPES, ALL),
    "t_piles_surgery": (15000, COMMON_TYPES, CORE),
    "t_thyroid_surgery": (30000, COMMON_TYPES, CORE + ["Hyderabad"]),
    "t_root_canal": (3500, COMMON_TYPES, ALL),
    "t_chemotherapy_session": (12000, COMMON_TYPES, CORE + ["Hyderabad", "Pune"]),
    "t_typhoid_treatment": (15000, COMMON_TYPES, ALL),
    "t_dengue_treatment": (18000, COMMON_TYPES, ALL),
    "t_turp_prostate": (35000, COMMON_TYPES, CORE),
    "t_lasik": (22000, PRIVATE_ONLY, CORE + ["Hyderabad", "Pune"]),
    "t_diagnostic_angiography": (12000, COMMON_TYPES, ALL),
    "t_gastroenteritis": (14000, COMMON_TYPES, CORE + ["Hyderabad", "Kolkata"]),
    "t_discectomy": (60000, SURGERY_TYPES, CORE),
    "t_copd_exacerbation": (20000, COMMON_TYPES, CORE + ["Kolkata"]),
}

SAMPLE_RANGES = {
    "govt": (120, 420),
    "private_low": (40, 150),
    "private_mid": (20, 95),
    "private_high": (6, 34),
}

SOURCE = (
    "SAMPLE DATA - model-derived from a base-rate table with city/hospital-type "
    "multipliers; NOT sourced from real invoices. Replace with CGHS/PM-JAY/state "
    "tariff data before production use."
)


def _rand(*parts: object) -> float:
    """Deterministic float in [0, 1) from a stable hash of the given parts."""
    h = hashlib.sha256("::".join(str(p) for p in parts).encode()).hexdigest()
    return int(h[:12], 16) / 0xFFFFFFFFFFFF


def build() -> list[dict]:
    rows: list[dict] = []
    n = 0
    for tid, (base_avg, types, cities) in BASE.items():
        for city in cities:
            state, city_mult = CITIES[city]
            for htype in types:
                jitter = 0.9 + 0.2 * _rand(tid, city, htype)  # +/-10%
                avg = base_avg * TYPE_MULT[htype] * city_mult * jitter
                cost_min = avg * (0.70 + 0.06 * _rand("min", tid, city, htype))
                cost_max = avg * (1.28 + 0.14 * _rand("max", tid, city, htype))

                lo, hi = SAMPLE_RANGES[htype]
                sample = int(lo + (hi - lo) * _rand("n", tid, city, htype))

                year_roll = _rand("year", tid, city, htype)
                data_year = 2026 if year_roll > 0.55 else 2025 if year_roll > 0.25 else 2024
                if htype in ("private_high",) and year_roll < 0.15:
                    data_year = 2023

                n += 1
                rows.append(
                    {
                        "id": f"cr_{n:04d}",
                        "treatment_id": tid,
                        "city": city,
                        "state": state,
                        "hospital_type": htype,
                        "cost_min": int(round(cost_min, -2)),
                        "cost_max": int(round(cost_max, -2)),
                        "cost_avg": int(round(avg, -2)),
                        "sample_size": sample,
                        "source": SOURCE,
                        "data_year": data_year,
                    }
                )
    return rows


if __name__ == "__main__":
    data = build()
    out = SEED_DIR / "cost_records.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(data)} rows -> {out}")
