import duckdb
import pytest

SCHEMA= """
CREATE TABLE person (
    person_id INTEGER, gender_concept_id INTEGER,
    year_of_birth INTEGER, month_of_birth INTEGER, day_of_birth INTEGER
);
CREATE TABLE observation_period (
    person_id INTEGER, gender_concept_id INTEGER, observation_period_start_date DATE, observation_period_end_date DATE
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