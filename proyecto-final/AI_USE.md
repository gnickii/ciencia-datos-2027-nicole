# Declaración de uso de inteligencia artificial

Proyecto final, Ciencia de Datos 2027 (Modalidad A: caracterización de una cohorte de epilepsia en OMOP).

## Herramientas

| Herramienta | Para qué se usó |
|---|---|
| Claude (Anthropic), en un Proyecto de claude.ai dedicado al curso | Tutoría paso a paso: explicar OMOP, SQL, pytest, Docker, CI y dbt; revisar errores pegados desde la terminal; proponer cambios al código |
| Claude Code (Anthropic), instalado en mi computadora | Redactar el primer borrador del `README.md` a partir del código del repositorio |

## Qué hizo la IA

- **Explicación y guía.** Me explicó qué hace cada paso y dónde ejecutarlo (terminal o editor) y me dio el código completo para escribir cada archivo.
- **Diagnóstico de errores.** A partir de los mensajes de `pytest`, `ruff`, Docker, GitHub Actions y dbt que pegué, señaló la causa (por ejemplo, una columna mal escrita en una consulta SQL, una coma faltante en datos de prueba, un `Dockerfile` con mayúsculas distintas).
- **Rediseño del análisis a partir de lo que encontré en los datos.** Al revisar los datos reales detecté que la lista de antiepilépticos era muy corta; con la IA decidimos definirlos por clase ATC N03, excluir la eclampsia (que SNOMED cuelga de "trastorno convulsivo") y abrir la base en solo lectura. La propuesta se probó primero en una copia de pruebas y después la apliqué yo.
- **Documentación.** Claude Code redactó el primer borrador del README; después se agregaron con Claude las secciones de datos, decisiones de diseño y limitaciones. Esas dos últimas incluyen una consulta de diagnóstico sobre la base (solo lectura) que se ejecutó para explicar por qué se perdían 100 personas.

## Qué hice yo

- Escribí y ejecuté los archivos del proyecto en mi computadora (SQL, módulos de Python, pruebas, Dockerfile, flujo de CI) siguiendo la guía.
- Generé la población con Synthea v3.0.0, descargué los vocabularios de Athena, corrí dbt-synthea y construí `data/omop.duckdb`.
- Ejecuté las pruebas, `ruff`, la CLI y las variantes de sensibilidad, y revisé los resultados.
- Hice los commits y manejé el repositorio.
- Escribí yo el código de cada archivo del proyecto, siguiendo el código completo que me dio la IA, y corregí mis propios errores de escritura a partir de los mensajes de `pytest` y `ruff`.

## Cómo verifiqué el trabajo

- 37 pruebas automatizadas con `pytest` sobre una base OMOP de juguete con casos de frontera (edad, ventana de observación, ventana del fármaco).
- `ruff check .` sin errores y CI en GitHub Actions.
- Las cifras del README se compararon con los CSV generados en `resultados/`.
- Las decisiones de diseño y las limitaciones se contrastaron con consultas a la base real (por ejemplo, la exclusión de eclampsia y la causa de las 100 personas fuera de observación).

## Qué sé explicar

Puedo explicar, sin ayuda de la IA:

- **La definición de la cohorte.** La fecha índice es el primer diagnóstico de epilepsia, y los cuatro criterios se aplican en orden (diagnósticos, edad, observación previa y antiepiléptico en el año siguiente). Cada criterio es un parámetro y cada variante de sensibilidad cambia uno solo.
- **Cómo se arman los conjuntos de conceptos.** Con `concept_ancestor` se toman los descendientes de epilepsia (SNOMED) y de los antiepilépticos (ATC N03 → ingredientes RxNorm), y por qué se excluye la eclampsia.
- **La tabla de atrición y de dónde sale cada cifra:** 11,548 → 424 → 424 → 183 → 103, y por qué el paso de observación previa es el que más personas elimina (en Synthea la observación empieza en la primera visita).
- **Por qué hay solo dos antiepilépticos** en los resultados (el simulador solo receta carbamazepina y clonazepam) y qué limita eso.
- **Cómo funcionan las pruebas:** una base OMOP de juguete con casos de frontera, y por qué las tablas de la cohorte son temporales y la base se abre en solo lectura.
- **Cómo se generaron los datos:** Synthea → dbt-synthea → `omop.duckdb`, con las banderas, la versión y las semillas documentadas en el README.

## Limitaciones del uso de IA

- La IA puede equivocarse (en este proyecto hubo errores de sintaxis y de nombres de columnas que se corrigieron al ejecutar las pruebas).
- Todo número y comando del README se revisó contra la salida real antes de aceptarlo.
- Los datos son sintéticos; ningún dato de pacientes reales se compartió con la IA.
