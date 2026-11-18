# Cohorte de epilepsia sobre OMOP CDM (datos sintéticos)

Proyecto final del curso de Ciencia de Datos 2027. Construye y caracteriza una
cohorte de personas con epilepsia que inician un antiepiléptico, usando datos
sintéticos de [Synthea](https://github.com/synthetichealth/synthea) transformados
al modelo común de datos [OMOP CDM](https://ohdsi.github.io/CommonDataModel/) y
consultados con [DuckDB](https://duckdb.org/).

> Todos los datos son **sintéticos**. Los resultados sirven para practicar el
> método, no para sacar conclusiones clínicas.

## Pregunta

En personas con un diagnóstico de epilepsia, ¿cuántas inician un antiepiléptico
en el año siguiente al diagnóstico, cómo se distribuyen por sexo y edad, y cuál
es el primer antiepiléptico que reciben?

## Definición de la cohorte

| Elemento | Definición |
|---|---|
| **Epilepsia** | Conceptos SNOMED *Epilepsy* (`84757009`) y *Seizure disorder* (`128613002`) con todos sus descendientes, excluyendo *Eclampsia in pregnancy* y sus descendientes. |
| **Antiepilépticos** | Ingredientes RxNorm que descienden de la clase ATC `N03` (*Antiepileptics*). |
| **Fecha índice** | Fecha del primer diagnóstico de epilepsia. |

Criterios, aplicados en orden (cada paso queda en la tabla de atrición):

1. Al menos `min_dx` diagnósticos de epilepsia.
2. Edad ≥ `min_age` años en la fecha índice.
3. Observación continua de al menos `prior_days` días antes de la fecha índice.
4. Inicio de un antiepiléptico (`drug_era`) dentro de los `followup_days` días posteriores a la fecha índice.

### Análisis principal y de sensibilidad

Cada variante cambia **un solo** parámetro respecto al análisis principal:

| Variante | `min_dx` | `min_age` | `prior_days` | `followup_days` |
|---|---|---|---|---|
| `principal` | 1 | 0 | 365 | 365 |
| `solo_adultos` | 1 | **18** | 365 | 365 |
| `dos_diagnosticos` | **2** | 0 | 365 | 365 |
| `observacion_180` | 1 | 0 | **180** | 365 |
| `sin_observacion_previa` | 1 | 0 | **0** | 365 |

## Resultados (base de 11 548 personas)

Atrición del análisis principal:

| Paso | Criterio | Personas | Excluidas |
|---|---|---:|---:|
| 0 | Todas las personas en la base OMOP | 11 548 | — |
| 1 | ≥ 1 diagnóstico de epilepsia | 424 | 11 124 |
| 2 | Edad ≥ 0 años en la fecha índice | 424 | 0 |
| 3 | ≥ 365 días de observación previa | 183 | 241 |
| 4 | Antiepiléptico dentro de 365 días | **103** | 80 |

Cohorte principal (n = 103): 53,4 % hombres y 46,6 % mujeres; 63,1 % de 0–17 años,
31,1 % de 18–64 y 5,8 % de 65 o más. El primer antiepiléptico fue carbamazepina
(51,5 %) o clonazepam (48,5 %).

Tamaño final de la cohorte en cada variante:

| Variante | n final |
|---|---:|
| `principal` | 103 |
| `solo_adultos` | 38 |
| `dos_diagnosticos` | 55 |
| `observacion_180` | 123 |
| `sin_observacion_previa` | 153 |

El criterio que más reduce la cohorte es la observación previa: el 57 % de las
personas con epilepsia no tiene 365 días de observación previa (artefacto de
Synthea, ver Limitaciones).

## Estructura

```
proyecto-final/
├── sql/
│   ├── 01_concept_sets.sql     # listas de conceptos: epilepsia y antiepilépticos
│   ├── 02_cohorte.sql          # criterios paso a paso + tabla de atrición
│   └── 03_caracterizacion.sql  # tablas por sexo, edad y primer antiepiléptico
├── src/epilepsia_omop/
│   ├── db.py                   # conexión a DuckDB en solo lectura
│   ├── cohort.py               # parámetros (CohortParams) y ejecución del SQL
│   ├── characterize.py         # arma las tablas descriptivas
│   └── cli.py                  # línea de comandos y variantes de sensibilidad
├── scripts/                    # exploración rápida de la base OMOP
├── tests/                      # pruebas con una base OMOP de juguete en memoria
├── data/                       # omop.duckdb (no se versiona)
├── resultados/<variante>/      # CSV generados (no se versionan)
├── Dockerfile
└── compose.yml
```

Los archivos SQL usan marcadores `{{min_dx}}`, `{{min_age}}`, `{{prior_days}}` y
`{{followup_days}}`, que `cohort.render_sql` reemplaza con los valores de
`CohortParams` (solo acepta enteros y falla si queda algún marcador sin reemplazar).

## Datos

La base OMOP no está en el repositorio. Para reproducirla:

1. **Synthea v3.0.0** (la versión que exige dbt-synthea), población de 10,000 vivos:
   `-p 10000 -s 42 -cs 42 -r 20260101`, exportando CSV (`--exporter.csv.export=true`,
   FHIR desactivado). Resultado: 11,548 personas, de las cuales 1,548 están fallecidas.
2. **Vocabularios** de [Athena](https://athena.ohdsi.org/) (SNOMED, RxNorm y ATC, entre otros).
3. **OHDSI/dbt-synthea** con dbt-duckdb, corrido desde su propio entorno (`dbt-env`):
   `dbt seed` y `dbt run` (87 modelos, 0 errores). No abrir `omop.duckdb` desde otro
   proceso mientras dbt corre.
4. Guardar el resultado como `data/omop.duckdb`.

Si la base tiene el esquema `dbt_synthea_dev`, la conexión lo usa
automáticamente. La base siempre se abre en **solo lectura**: las tablas de la
cohorte se crean como tablas temporales.

Para revisar que la base tenga lo necesario:

```bash
python scripts/explorar_omop.py [ruta/a/omop.duckdb]
```

## Decisiones de diseño

- **Eclampsia excluida.** En SNOMED *Eclampsia in pregnancy* es descendiente de
  *Seizure disorder*, pero no es epilepsia; sin la exclusión entraban personas que
  no corresponden a la pregunta.
- **Antiepilépticos por clase ATC N03**, no por una lista corta de nombres, para que
  cualquier fármaco del grupo cuente.
- **Todas las edades** (`min_age = 0`): la epilepsia simulada es sobre todo pediátrica
  (63 % de la cohorte tiene 0–17 años); con solo adultos quedarían 38 personas.

## Limitaciones

- **Datos sintéticos.** La prevalencia simulada (424 de 11,548, ≈ 3.7 %) es mucho mayor
  que la real; no sirve para estimar epidemiología.
- **Solo dos antiepilépticos.** El módulo de epilepsia de Synthea solo receta
  carbamazepina y clonazepam. La definición por ATC N03 cubre todo el grupo, pero
  levetiracetam, lamotrigina, valproato, etc. no aparecen en los datos.
- **Observación previa.** En Synthea el periodo de observación empieza en el primer
  encuentro de cada persona, por lo que quien se diagnostica al inicio de su historia
  no puede tener 365 días previos (424 → 183). Es un artefacto del simulador.
- **Fechas índice un día antes de la observación.** Incluso con `prior_days = 0` se
  pierden 100 personas. En todas, el diagnóstico de epilepsia es su primera condición
  y está fechado **un día antes** de su primera visita, que es donde dbt-synthea
  inicia el periodo de observación (en toda la base el inicio de observación coincide
  con la primera visita). Es una inconsistencia de fechas del simulador, no un error
  de la consulta; no se corrigió para no alterar el criterio de observación.
- **Clonazepam** es una benzodiacepina dentro de ATC N03; en la simulación puede no
  usarse solo como antiepiléptico.

## Uso

Requiere Python ≥ 3.11.

```bash
cd proyecto-final
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -e ".[dev]"
```

Correr la cohorte:

```bash
python -m epilepsia_omop.cli                      # análisis principal
python -m epilepsia_omop.cli --variante todas     # principal + sensibilidad
python -m epilepsia_omop.cli --variante solo_adultos --db otra.duckdb --out salida/
```

Cada variante escribe en `resultados/<variante>/`:

- `attrition.csv`: personas que quedan y se excluyen en cada paso.
- `table1_sexo.csv`, `table1_edad.csv`: distribución de la cohorte.
- `primer_aed.csv`: primer antiepiléptico dentro de la ventana de seguimiento.

## Pruebas y estilo

```bash
pytest
ruff check .
```

Las pruebas no necesitan la base real: `tests/conftest.py` arma una base OMOP
mínima en memoria con casos controlados.

## Docker

```bash
docker compose run --rm pruebas    # corre pytest
docker compose run --rm cohorte    # corre todas las variantes con ./data y ./resultados montados
```

## Integración continua

GitHub Actions (`.github/workflows/proyecto-final.yml`) corre `ruff`, `pytest` y
las pruebas dentro de Docker en cada push o pull request que toque
`proyecto-final/`.
