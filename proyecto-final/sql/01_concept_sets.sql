--Conceptos válidos como epilepsia (concepto raíz y todos sus descendientes)
CREATE OR REPLACE TABLE cs_epilepsia AS
SELECT DISTINCT ca.descendant_concept_id AS concept_id
FROM concept AS c
JOIN concept_ancestor AS ca
  ON ca.ancestor_concept_id = c.concept_id
WHERE c.vocabulary_id = 'SNOMED'
  AND c.concept_code IN ('84757009', '128613002');

-- Conceptos que cuentan como fármaco antiepiléptico
CREATE OR REPLACE TABLE cs_antiepilepticos AS
SELECT DISTINCT concept_id
FROM concept
WHERE vocabulary_id = 'RxNorm'
  AND concept_class_id = 'Ingredient'
  AND lower(concept_name) IN ('levetiracetam', 'lamotrigine');