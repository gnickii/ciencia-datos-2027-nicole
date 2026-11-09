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
HAVING count(*)>=1;

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
WHERE age_at_index >= 18;
