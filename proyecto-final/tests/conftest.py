import duckdb
import pytest

SCHEMA= """
CREATE TABLE person (
    person_id INTEGER, gender_concept_id INTEGER,
    year_of_birth INTEGER, month_of_birth INTEGER, day_of_birth INTEGER
);
CREATE TABLE observation_period (
  person_id INTEGER, observation_period_start_date DATE, observation_period_end_date DATE
);
CREATE TABLE condition_occurrence (
    person_id INTEGER, condition_concept_id INTEGER, condition_start_date DATE
);
CREATE TABLE drug_era (
    person_id INTEGER, drug_concept_id INTEGER, drug_era_start_date DATE
);
CREATE TABLE concept (
    concept_id INTEGER, concept_name VARCHAR, vocabulary_id VARCHAR, 
    concept_class_id VARCHAR, concept_code VARCHAR
);
CREATE TABLE concept_ancestor (ancestor_concept_id INTEGER, descendant_concept_id INTEGER);

"""

DATOS= """
INSERT INTO concept VALUES
    (1000, 'Epilepsy',      'SNOMED', 'CLinical Finding', '84757009'),
    (1001, 'Focal Epilepsy','SNOMED', 'Clinical Finding', '999001'),
    (1002, 'Hypertension',  'SNOMED', 'Clinical FInding', '38341003'),
    (2001, 'Levetiracetam', 'RxNorm', 'Ingredient',       '114477'),
    (2002, 'Lamotrigine',   'RxNorm', 'Ingredient',       '28439'),
    (2003, 'Lisinopril',    'RxNorm', 'Ingredient',       '29046');

INSERT INTO concept_ancestor VALUES
    (1000,1000), (1001,1001),(1002,1002),
    (1000,1001);

INSERT INTO person VALUES
    (1, 8532, 1980, 5, 10),
    (2, 8507, 2015, 1, 1),
    (3, 8507, 1975, 3, 3),
    (4, 8532, 1990, 7, 7),
    (5, 8507, 1960, 1, 1),
    (6, 8532, 1985, 9, 9),
    (7, 8507, 1970, 12,12);

INSERT INTO observation_period VALUES
    (1, '2018-01-01', '2024-12-31'),
    (2, '2018-01-01', '2024-12-31'),
    (3, '2020-03-01', '2024-12-31'),
    (4, '2018-01-01', '2024-12-31'),
    (5, '2018-01-01', '2024-12-31'),
    (6, '2018-01-01', '2024-12-31'),
    (7, '2018-01-01', '2024-12-31');

INSERT INTO condition_occurrence VALUES
    (1, 1000, '2020-06-01'), (1, 1000, '2021-02-01'),
    (2, 1000, '2020-06-01'),
    (3, 1000, '2020-06-01'),
    (4, 1000, '2020-06-01'),
    (5, 1002, '2020-06-01'),
    (6, 1001, '2020-06-01'), (6, 1001, '2020-09-01'),
    (7, 1000, '2020-06-01');

INSERT INTO  drug_era VALUES
    (1, 2001, '2020-06-11'),
    (2, 2001, '2020-06-11'),
    (3, 2001, '2020-06-11'),
    (4, 2003, '2020-06-11'),
    (6, 2002, '2020-07-01'),
    (7, 2001, '2020-06-20');
"""

@pytest.fixture
def con():
    conexion =duckdb.connect(":memory:")
    conexion.execute (SCHEMA) 
    conexion.execute (DATOS)
    yield conexion
    conexion.close()
