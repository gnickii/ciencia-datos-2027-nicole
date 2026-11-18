"""Conexión a la base OMOP en DuckDB (solo lectura)."""
from pathlib import Path

import duckdb

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "omop.duckdb"
OMOP_SCHEMA = "dbt_synthea_dev"


def connect(path=None) -> duckdb.DuckDBPyConnection:
    """Abre la base en solo lectura y apunta al esquema de dbt si existe."""
    ruta = Path(path) if path else DEFAULT_DB
    if not ruta.exists():
        raise FileNotFoundError(
            f"No encuentro la base OMOP en {ruta}. Pásala con --db."
        )
    con = duckdb.connect(str(ruta), read_only=True)
    esquemas = {
        r[0]
        for r in con.execute(
            "SELECT schema_name FROM information_schema.schemata"
        ).fetchall()
    }
    if OMOP_SCHEMA in esquemas:
        con.execute(f"SET schema = '{OMOP_SCHEMA}'")
    return con