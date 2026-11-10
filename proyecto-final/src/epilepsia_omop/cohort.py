"""Construcción de una cohorte de epilepsia sobre una base OMOP en DuckDB"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import duckdb
import pandas as pd

# La carpeta sql/ está dos niveles arriba de este archivo: src/epilepsia_omop/cohort.py
SQL_DIR= Path(__file__).resolve().parents[2] /"sql"

@dataclass(frozen=True)
class CohortParams:
    """Los numeros de la definición de cohorte"""

    min_dx: int=1 #minimo de diagnosticos de epilepsia
    min_age: int= 0 #
    prior_days: int= 365 #días de observación previa a la fecha índice 
    followup_days: int= 365 #ventana después de la fecha índice para iniciar antiepiléptico

def render_sql(sql: str,params: CohortParams) -> str:
    """ Reemplaza cada marcador {{...}} del sql con el valor del parámetro"""
    for nombre, valor in asdict (params).items():
        if not isinstance (valor,int):
            raise TypeError(f'El parámetro {nombre} debe ser entero, no {type(valor).__name__}')
        sql = sql.replace ("{{"+ nombre +"}}", str (valor))
    if "{{" in sql:
        raise ValueError(f'Quedan marcadores {{...}} sin reemplazar en el SQL')
    return sql

def run_script(con: duckdb.DuckDBPyConnection, nombre: str, params: CohortParams)-> None:
     """Lee un archivo de sql/, reemplaza los parámetros y lo ejecuta"""
     texto = (SQL_DIR/nombre).read_text(encoding="utf-8")
     con.execute(render_sql(texto,params))

def build_cohort(
        con:duckdb.DuckDBPyConnection,params:CohortParams | None=None
) -> pd.DataFrame:
    """Crea las tablas 'cohort' y 'atricion' y devuelve la tabla de atrición"""
    params =params or CohortParams()
    run_script(con, "01_concept_sets.sql", params)
    run_script(con, "02_cohorte.sql",params)
    return con.execute("SELECT * FROM attrition ORDER BY step").df()