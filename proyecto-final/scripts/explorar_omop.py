"""Revisión rápida de la base OMOP: ¿tiene lo que necesita la cohorte de epilepsia?

Uso (desde proyecto-final/):  python scripts/explorar_omop.py
Solo LEE la base; no modifica nada.
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parents[1]
DB = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "data" / "omop.duckdb"
CSV_MEDS = RAIZ / "data" / "synthea" / "poblacion10000" / "csv" / "medications.csv"
ESQUEMA = "dbt_synthea_dev"

con = duckdb.connect(str(DB), read_only=True)
esquemas = {r[0] for r in con.execute("SELECT schema_name FROM information_schema.schemata").fetchall()}
if ESQUEMA in esquemas:
    con.execute(f"SET schema = '{ESQUEMA}'")


def q(titulo: str, sql: str) -> None:
    print(f"\n=== {titulo}")
    try:
        print(con.sql(sql))
    except Exception as e:  # noqa: BLE001 - queremos ver el error y seguir
        print(f"  (falló: {e})")


q("Esquemas en la base", "SELECT schema_name FROM information_schema.schemata ORDER BY 1")

q(
    "Filas de las tablas que usa la cohorte",
    """
    SELECT 'person' AS tabla, count(*) AS filas FROM person
    UNION ALL SELECT 'observation_period', count(*) FROM observation_period
    UNION ALL SELECT 'condition_occurrence', count(*) FROM condition_occurrence
    UNION ALL SELECT 'drug_era', count(*) FROM drug_era
    UNION ALL SELECT 'concept', count(*) FROM concept
    UNION ALL SELECT 'concept_ancestor', count(*) FROM concept_ancestor
    """,
)

q(
    "Conceptos de epilepsia (SNOMED 84757009 y 128613002)",
    """
    SELECT concept_id, concept_name, vocabulary_id
    FROM concept
    WHERE vocabulary_id = 'SNOMED' AND concept_code IN ('84757009', '128613002')
    """,
)

q(
    "Personas con epilepsia (incluyendo descendientes)",
    """
    SELECT count(DISTINCT co.person_id) AS personas
    FROM condition_occurrence AS co
    JOIN concept_ancestor AS ca ON ca.descendant_concept_id = co.condition_concept_id
    JOIN concept AS c ON c.concept_id = ca.ancestor_concept_id
    WHERE c.vocabulary_id = 'SNOMED' AND c.concept_code IN ('84757009', '128613002')
    """,
)

q(
    "Antiepilépticos candidatos presentes en drug_era (personas)",
    """
    SELECT c.concept_name AS ingrediente, c.concept_class_id, count(DISTINCT de.person_id) AS personas
    FROM drug_era AS de
    JOIN concept AS c ON c.concept_id = de.drug_concept_id
    WHERE lower(c.concept_name) IN (
      'levetiracetam','lamotrigine','carbamazepine','valproate','valproic acid','phenytoin',
      'topiramate','oxcarbazepine','lacosamide','phenobarbital','gabapentin','clonazepam',
      'zonisamide','primidone','ethosuximide','clobazam','pregabalin')
    GROUP BY 1, 2 ORDER BY personas DESC
    """,
)

if CSV_MEDS.exists():
    q(
        "Qué receta Synthea cuando el motivo es epilepsia (CSV original)",
        f"""
        SELECT DESCRIPTION, count(DISTINCT PATIENT) AS personas
        FROM read_csv('{CSV_MEDS.as_posix()}')
        WHERE CAST(REASONCODE AS VARCHAR) IN ('84757009', '128613002')
        GROUP BY 1 ORDER BY personas DESC
        """,
    )
    