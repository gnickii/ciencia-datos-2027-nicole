-- Todos los diagnósticos de epilepsia de de cada persona 
-- Une los diganosticos con la lista cs_epilepsia (creada en 01_concept_sets.sql
CREATE OR REPLACE TABLE dx_epilepsia AS
SELECT co.person_id, co.condition_start_date AS dx_date
FROM condition_occurrence AS co
JOIN cs_epilepsia AS cs
ON cs.concept_id= co.condition_concept_id;

--Paso 1: personas con epilepsia
-- La fecha índice es la fecha de su primer diagnóstico.
CREATE OR REPLACE TABLE cohort_step1 AS
SELECT
    person_id,
    min(dx_date) AS index_date,
    count(*) AS n_dx
FROM dx_epilepsia
GROUP BY person_id
HAVING count(*)>= {{min_dx}};

-- Paso 2: edad en la fecha índice (años completos). Solo se quedan mayores de edad
CREATE OR REPLACE TABLE cohort_step2 AS
WITH con_edad AS (
    SELECT
        s.person_id,
        s.index_date,
        s.n_dx,
        p.gender_concept_id,
        date_sub(
            'year',
            make_date(
                p.year_of_birth,
                coalesce(p.month_of_birth,1),
                coalesce(p.day_of_birth, 1)
            ),
            s.index_date
        ) AS age_at_index
        FROM cohort_step1 AS s 
        JOIN person AS p USING (person_id)
)
SELECT *
FROM con_edad
WHERE age_at_index >= {{min_age}};


--Paso 3:Observación continua previa a la fecha índice (365 días)
CREATE OR REPLACE TABLE cohort_step3 AS
SELECT s.*
FROM cohort_step2 AS s
WHERE EXISTS (
  SELECT 1
  FROM observation_period AS op
  WHERE op.person_id = s.person_id
    AND op.observation_period_start_date <= s.index_date - INTERVAL {{prior_days}} DAY
      AND op.observation_period_end_date   >= s.index_date
);

--Paso 4: Inicia un antiepiléptico dentro de los 365 días posteriores a la fecha índice
CREATE OR REPLACE TABLE cohort_step4 AS 
SELECT s.*
FROM cohort_step3 AS s
WHERE EXISTS (
    SELECT 1
    FROM drug_era AS de
    JOIN cs_antiepilepticos AS cs
      ON cs.concept_id = de.drug_concept_id
    WHERE de.person_id =s.person_id 
      AND de.drug_era_start_date >= s.index_date
      AND de.drug_era_start_date <= s.index_date + INTERVAL {{followup_days}} DAY
);

-- Cohorte final: quién cumplió los cuatro criterios
CREATE OR REPLACE TABLE cohort AS
SELECT 
    person_id,
    index_date,
    age_at_index,
    CASE gender_concept_id
        WHEN 8507 THEN 'M'
        WHEN 8532 THEN 'F'
        ELSE 'otro/desconocido'
    END AS sex,
    n_dx
FROM cohort_step4;


--Tabla de atrición: Personas que quedan tras cada paso
CREATE OR REPLACE TABLE attrition AS 
WITH steps AS (
    SELECT 0 AS step, 'Todas las personas en la base OMOP' AS description,
         (SELECT count(DISTINCT person_id) FROM person) AS n_persons
    UNION ALL 
    SELECT 1, 'Con al menos {{min_dx}} diagnóstico(s) de epilepsia', (SELECT count(*) FROM cohort_step1)
    UNION ALL
    SELECT 2, 'Edad >= {{min_age}} años en la fecha índice', (SELECT count(*)FROM cohort_step2)
    UNION ALL
    SELECT 3, '>= {{prior_days}} días de observación previa', (SELECT count(*) FROM cohort_step3)
    UNION ALL
    SELECT 4, 'Antiepiléptico dentro de {{followup_days}} días tras la fecha índice',
           (SELECT count(*) FROM cohort_step4)
)
SELECT 
    step,
    description,
    n_persons,
    coalesce(lag(n_persons) OVER (ORDER BY step) - n_persons,0) AS n_excluded
    FROM steps
    ORDER BY step;