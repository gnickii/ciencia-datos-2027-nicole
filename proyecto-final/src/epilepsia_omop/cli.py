"""Línea de comandos: contstruye la cohorte y guarda las tablasen CSV"""

from __future__ import annotations

import argparse
from pathlib import Path

from epilepsia_omop.characterize import characterize
from epilepsia_omop.cohort import CohortParams
from epilepsia_omop.db import connect

# Análisis principal + variantes de sensibilidad:cada una cambia UN parámetro
VARIANTES: dict[str, CohortParams] = {
    "principal": CohortParams(),
    "solo_adultos": CohortParams (min_age=18),
    "dos_diagnosticos": CohortParams (min_dx=2),
    "observacion_180": CohortParams (prior_days=180),
    "sin_observacion_previa": CohortParams (prior_days=0),
}

RESULTADOS = Path(__file__).resolve().parents[2] / "resultados" 

def run_variant(nombre: str, db: Path | str | None, out_dir: Path) ->Path:
    """Corre una variante y guarda atricion y tablas descriptivas en out_dir/<nombre/.>"""
    params = VARIANTES [nombre]
    con= connect(db)
    try:
        tablas = characterize(con, params)
        tablas["attrition"]= con.execute("SELECT * FROM attrition ORDER BY step").df()
    finally:
        con.close()
    destino= out_dir / nombre
    destino.mkdir(parents=True, exist_ok= True)
    for tabla, df in tablas.items():
        df.to_csv(destino / f'{tabla}.csv',index= False)
    return destino

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Cohorte de epilepsia sobre OMOP (DuckDB)")
    parser.add_argument(
        "--variante",
        choices=[*VARIANTES, "todas"],
        default="principal",
        help="Qué definición de cohorte correr (por defecto: principal)",
    )
    parser.add_argument("--db", default=None, help="Ruta a la base .duckdb (por defecto data/omop.duckdb)")
    parser.add_argument("--out", default=str(RESULTADOS), help="Carpeta donde guardar los CSV")
    args = parser.parse_args(argv)

    nombres = list(VARIANTES) if args.variante == "todas" else [args.variante]
    for nombre in nombres:
        destino = run_variant(nombre, args.db, Path(args.out))
        print(f"[{nombre}] resultados en {destino}")


if __name__ == "__main__":
    main()