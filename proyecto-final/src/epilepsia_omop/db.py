"""Conexion a la base OMOP en DuckDB"""

from __future__ import annotations

from pathlib import Path

import duckdb

# data/OMOP.duckdb, en la raíz de proyecto-final
DEFAULT_DB= Path (__file__).resolve().parents[2] / "data" / "OMOP.duckdb"


def connect (path: Path | str | None= None) -> duckdb.DuckDBPyConnection:
    """Abre la base OMOP. Fala si el archivo no existe"""
    ruta = Path (path) if path else DEFAULT_DB
    if not ruta.exists():
        raise FileNotFoundError(
            f'No encuentra la base OMOP en {ruta}.'
            "Genera los datos con Synthea + ETL-Synthea o indica otra ruta con --db."
        )
    return duckdb.connect(str(ruta))

