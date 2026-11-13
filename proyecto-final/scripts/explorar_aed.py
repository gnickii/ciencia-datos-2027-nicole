"""¿Qué cuenta como 'antiepiléptico' y como 'epilepsia' en esta base? (solo lee la base)

Uso (desde proyecto-final/):  python scripts/explorar_aed.py
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
    except Exception as e:  # noqa: BLE001
        print(f"  (falló: {e})")


q(
    "1. ¿Está la clasificación ATC 'N03 Antiepilépticos' en los vocabularios?",
    """
    SELECT concept_id, concept_code, concept_name, concept_class_id
    FROM concept
    WHERE vocabulary_id = 'ATC' AND concept_code IN ('N03', 'N03A')
    """,
)

q(
    "2. Ingredientes de ATC N03 que aparecen en drug_era (personas)",
    """
    SELECT c.concept_name AS ingrediente, count(DISTINCT de.person_id) AS personas
    FROM drug_era AS de
    JOIN concept_ancestor AS ca ON ca.descendant_concept_id = de.drug_concept_id
    JOIN concept AS atc ON atc.concept_id = ca.ancestor_concept_id
    JOIN concept AS c ON c.concept_id = de.drug_concept_id
    WHERE atc.vocabulary_id = 'ATC' AND atc.concept_code = 'N03'
    GROUP BY 1 ORDER BY personas DESC
    """,
)

q(
    "3. Qué diagnósticos componen la 'epilepsia' de tu concept set (personas)",
    """
    SELECT c2.concept_name AS diagnostico, count(DISTINCT co.person_id) AS personas
    FROM condition_occurrence AS co
    JOIN concept_ancestor AS ca ON ca.descendant_concept_id = co.condition_concept_id
    JOIN concept AS c ON c.concept_id = ca.ancestor_concept_id
    JOIN concept AS c2 ON c2.concept_id = co.condition_concept_id
    WHERE c.vocabulary_id = 'SNOMED' AND c.concept_code IN ('84757009', '128613002')
    GROUP BY 1 ORDER BY personas DESC
    """,
)

if CSV_MEDS.exists():
    q(
        "4. Por qué receta Synthea carbamazepina / clonazepam / pregabalina (CSV original)",
        f"""
        SELECT DESCRIPTION, REASONDESCRIPTION, count(DISTINCT PATIENT) AS personas
        FROM read_csv('{CSV_MEDS.as_posix()}')
        WHERE lower(DESCRIPTION) LIKE '%carbamazepine%'
           OR lower(DESCRIPTION) LIKE '%clonazepam%'
           OR lower(DESCRIPTION) LIKE '%pregabalin%'
        GROUP BY ALL ORDER BY personas DESC LIMIT 20
        """,
    )

    
q(
    "5. Conceptos SNOMED con 'eclampsia' en el nombre (para excluirlos)",
    """
    SELECT concept_id, concept_code, concept_name
    FROM concept
    WHERE vocabulary_id = 'SNOMED' AND lower(concept_name) LIKE '%eclampsia%'
    ORDER BY concept_code
    """,
)

q(
    "6. Personas: solo con los dos códigos exactos vs. incluyendo descendientes",
    """
    WITH base AS (
      SELECT concept_id FROM concept
      WHERE vocabulary_id = 'SNOMED' AND concept_code IN ('84757009', '128613002')
    ),
    exactos AS (
      SELECT DISTINCT person_id FROM condition_occurrence
      WHERE condition_concept_id IN (SELECT concept_id FROM base)
    ),
    todos AS (
      SELECT DISTINCT co.person_id
      FROM condition_occurrence AS co
      JOIN concept_ancestor AS ca ON ca.descendant_concept_id = co.condition_concept_id
      WHERE ca.ancestor_concept_id IN (SELECT concept_id FROM base)
    )
    SELECT (SELECT count(*) FROM exactos) AS codigos_exactos,
           (SELECT count(*) FROM todos) AS con_descendientes
    """,
)
q(
    "5. Conceptos SNOMED con 'eclampsia' en el nombre (para excluirlos)",
    """
    SELECT concept_id, concept_code, concept_name
    FROM concept
    WHERE vocabulary_id = 'SNOMED' AND lower(concept_name) LIKE '%eclampsia%'
    ORDER BY concept_code
    """,
)

q(
    "6. Personas: solo con los dos códigos exactos vs. incluyendo descendientes",
    """
    WITH base AS (
      SELECT concept_id FROM concept
      WHERE vocabulary_id = 'SNOMED' AND concept_code IN ('84757009', '128613002')
    ),
    exactos AS (
      SELECT DISTINCT person_id FROM condition_occurrence
      WHERE condition_concept_id IN (SELECT concept_id FROM base)
    ),
    todos AS (
      SELECT DISTINCT co.person_id
      FROM condition_occurrence AS co
      JOIN concept_ancestor AS ca ON ca.descendant_concept_id = co.condition_concept_id
      WHERE ca.ancestor_concept_id IN (SELECT concept_id FROM base)
    )
    SELECT (SELECT count(*) FROM exactos) AS codigos_exactos,
           (SELECT count(*) FROM todos) AS con_descendientes
    """,
)