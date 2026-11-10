"""Caracterización de la cohorte: tablas descriptivas (tabla 1)"""

from __future__ import annotations

import duckdb 
import pandas as pd

from epilepsia_omop.cohort import CohortParams, build_cohort, run_script

TABLAS= ('table1_sexo', 'table1_edad', 'primer_aed')


def characterize(
        con:duckdb.DuckDBPyConnection, params: CohortParams | None = None
) -> dict [str, pd.DataFrame]:
    """Construye la cohorte, corre la caracterización y devuelve las tablas"""
    params = params or CohortParams()
    build_cohort(con, params)
    run_script(con, "03_caracterizacion.sql", params)
    return {t: con.execute(f"SELECT * FROM {t}").df() for t in TABLAS}