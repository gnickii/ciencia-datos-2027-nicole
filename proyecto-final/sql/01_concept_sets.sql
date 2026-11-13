CREATE OR REPLACE TEMP TABLE cs_epilepsia AS
SELECT DISTINCT ca.descendant_concept_id AS concept_id
FROM concept AS c
JOIN concept_ancestor AS ca ON ca.ancestor_concept_id = c.concept_id
WHERE c.vocabulary_id = 'SNOMED'
  AND c.concept_code IN ('84757009', '128613002')
  AND ca.descendant_concept_id NOT IN (
    SELECT ex_ca.descendant_concept_id
    FROM concept AS ex
    JOIN concept_ancestor AS ex_ca ON ex_ca.ancestor_concept_id = ex.concept_id
    WHERE ex.vocabulary_id = 'SNOMED'
      AND ex.concept_name = 'Eclampsia in pregnancy'
  );

CREATE OR REPLACE TEMP TABLE cs_antiepilepticos AS
SELECT DISTINCT c.concept_id
FROM concept AS atc
JOIN concept_ancestor AS ca ON ca.ancestor_concept_id = atc.concept_id
JOIN concept AS c ON c.concept_id = ca.descendant_concept_id
WHERE atc.vocabulary_id = 'ATC'
  AND atc.concept_code = 'N03'
  AND c.vocabulary_id = 'RxNorm'
  AND c.concept_class_id = 'Ingredient';