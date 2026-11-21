# Diccionario de datos

Documenta las variables que produce el proyecto. Los datos de origen son sintéticos
(Synthea → OMOP CDM); ver `README.md` para su procedencia y versiones.

## Parámetros de la cohorte (`CohortParams`)

| Parámetro | Tipo | Valor principal | Significado |
|---|---|---|---|
| `min_dx` | entero | 1 | Número mínimo de diagnósticos de epilepsia por persona |
| `min_age` | entero (años) | 0 | Edad mínima en la fecha índice (0 = todas las edades) |
| `prior_days` | entero (días) | 365 | Observación continua requerida antes de la fecha índice |
| `followup_days` | entero (días) | 365 | Ventana posterior a la fecha índice para iniciar un antiepiléptico |

## Tabla `cohort` (temporal, una fila por persona)

| Variable | Tipo | Descripción |
|---|---|---|
| `person_id` | entero | Identificador de la persona en OMOP (sintético) |
| `index_date` | fecha | Fecha del primer diagnóstico de epilepsia (`condition_start_date` mínima) |
| `age_at_index` | entero (años) | Años completos entre la fecha de nacimiento y `index_date` |
| `sex` | texto | `F` (concepto 8532), `M` (8507) u `otro/desconocido` |
| `n_dx` | entero | Número de registros de diagnóstico de epilepsia de la persona |

## Archivos de salida (`resultados/<variante>/`)

### `attrition.csv`: tabla de atrición

| Variable | Tipo | Descripción |
|---|---|---|
| `step` | entero | Paso del embudo (0 a 4) |
| `description` | texto | Criterio aplicado en ese paso |
| `n_persons` | entero | Personas que quedan después del paso |
| `n_excluded` | entero | Personas excluidas respecto al paso anterior (0 en el paso 0) |

### `table1_sexo.csv`

| Variable | Tipo | Descripción |
|---|---|---|
| `sex` | texto | `F`, `M` u `otro/desconocido` |
| `n` | entero | Personas de la cohorte final |
| `pct` | decimal | Porcentaje sobre la cohorte final |

### `table1_edad.csv`

| Variable | Tipo | Descripción |
|---|---|---|
| `grupo_edad` | texto | `0-17`, `18-64` o `65+` años, según la edad en la fecha índice |
| `n` | entero | Personas de la cohorte final |
| `pct` | decimal | Porcentaje sobre la cohorte final |

### `primer_aed.csv`: primer antiepiléptico

| Variable | Tipo | Descripción |
|---|---|---|
| `medicamento` | texto | Nombre del ingrediente RxNorm del primer `drug_era` antiepiléptico iniciado dentro de la ventana de seguimiento |
| `n` | entero | Personas de la cohorte final |
| `pct` | decimal | Porcentaje sobre la cohorte final |

## Tablas OMOP usadas (esquema `dbt_synthea_dev`)

| Tabla | Variables usadas |
|---|---|
| `person` | `person_id`, `gender_concept_id`, `year_of_birth`, `month_of_birth`, `day_of_birth` |
| `observation_period` | `person_id`, `observation_period_start_date`, `observation_period_end_date` |
| `condition_occurrence` | `person_id`, `condition_concept_id`, `condition_start_date` |
| `drug_era` | `person_id`, `drug_concept_id`, `drug_era_start_date` |
| `concept` | `concept_id`, `concept_name`, `vocabulary_id`, `concept_class_id`, `concept_code` |
| `concept_ancestor` | `ancestor_concept_id`, `descendant_concept_id` |

## Conjuntos de conceptos

| Conjunto | Definición |
|---|---|
| `cs_epilepsia` | SNOMED `84757009` (Epilepsy) y `128613002` (Seizure disorder) y todos sus descendientes, excluyendo *Eclampsia in pregnancy* y sus descendientes |
| `cs_antiepilepticos` | Ingredientes RxNorm (`concept_class_id = 'Ingredient'`) que descienden de ATC `N03` (Antiepileptics) |
