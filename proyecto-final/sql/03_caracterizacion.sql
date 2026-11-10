--Tabla 1a: Cohorte por sexo 
CREATE OR REPLACE TABLE table1_sexo AS
SELECT 
    sex,
    count(*) AS n,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM cohort 
GROUP BY sex
ORDER BY sex;

--Tabla 1b: Cohorte por edad a la fecha índice
CREATE OR REPLACE TABLE table1_edad AS
SELECT
  CASE
    WHEN age_at_index < 18 THEN '0-17'
    WHEN age_at_index < 65 THEN '18-64'
    ELSE '65+'
  END AS grupo_edad,
  count(*) AS n,
  round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM cohort
GROUP BY grupo_edad
ORDER BY min(age_at_index);

--Tabla 2: primer antiepiléptico durante la primer ventana de tratamiento por paciente
CREATE OR REPLACE TABLE primer_aed AS
WITH aed_en_ventana AS (
  SELECT
    co.person_id,
    c.concept_name AS medicamento,
    row_number() OVER (
      PARTITION BY co.person_id
      ORDER BY de.drug_era_start_date, c.concept_name
    ) AS orden
  FROM cohort AS co
  JOIN drug_era AS de
    ON de.person_id = co.person_id
  JOIN cs_antiepilepticos AS cs
    ON cs.concept_id = de.drug_concept_id
  JOIN concept AS c
    ON c.concept_id = de.drug_concept_id
  WHERE de.drug_era_start_date >= co.index_date
    AND de.drug_era_start_date <= co.index_date + INTERVAL {{followup_days}} DAY
)
SELECT
  medicamento,
  count(*) AS n,
  round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM aed_en_ventana
WHERE orden = 1
GROUP BY medicamento
ORDER BY n DESC, medicamento;