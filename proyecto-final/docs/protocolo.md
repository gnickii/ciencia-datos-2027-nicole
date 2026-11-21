# Protocolo

## Pregunta

En personas con un diagnóstico de epilepsia, ¿cuántas inician un antiepiléptico en el
año siguiente al diagnóstico, cómo se distribuyen por sexo y edad, y cuál es el primer
antiepiléptico que reciben?

Es un estudio descriptivo (modalidad A: caracterización). No busca asociaciones ni
estimar prevalencia.

## Población y fuente de datos

Datos **sintéticos** de Synthea v3.0.0 (10,000 personas vivas generadas; 11,548 en la base
con las fallecidas), convertidos a OMOP CDM con OHDSI/dbt-synthea y consultados en DuckDB.
Las versiones y fechas están en el README.

## Definición de la cohorte

- **Fecha índice:** fecha del primer diagnóstico de epilepsia.
- **Epilepsia:** SNOMED *Epilepsy* y *Seizure disorder* con descendientes, sin *Eclampsia in pregnancy*.
- **Antiepilépticos:** ingredientes RxNorm descendientes de ATC N03.

Criterios, en orden, con su tabla de atrición:

1. Al menos `min_dx` diagnósticos de epilepsia.
2. Edad en la fecha índice ≥ `min_age`.
3. Observación continua de `prior_days` días antes de la fecha índice.
4. Un `drug_era` antiepiléptico que inicia entre la fecha índice y `followup_days` días después.

## Análisis

1. **Principal** (`min_dx = 1`, `min_age = 0`, `prior_days = 365`, `followup_days = 365`).
2. **Sensibilidad**, cambiando un parámetro a la vez: `solo_adultos`, `dos_diagnosticos`,
   `observacion_180` y `sin_observacion_previa`.

Para cada variante se reportan la tabla de atrición, la distribución por sexo y por
grupo de edad (0–17, 18–64, 65+) y el primer antiepiléptico. No se hacen pruebas
estadísticas: son conteos y porcentajes descriptivos.

## Limitaciones principales

Ver la sección *Limitaciones* del `README.md` (datos sintéticos, solo dos antiepilépticos
en la simulación, y artefactos del periodo de observación de Synthea).

## Variables y salidas

Ver `docs/features.md`.
