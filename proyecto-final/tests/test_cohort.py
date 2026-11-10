from pathlib import Path 
import pytest

from epilepsia_omop.cohort import CohortParams, build_cohort, render_sql

SQL_DIR= Path (__file__).resolve().parents[1]/"sql"

def correr_sql(con, nombre):
    """Lee un archivo de sql/, reemplaza los parámetros (adultos, 18 años) y lo ejecuta."""
    texto = (SQL_DIR / nombre).read_text(encoding="utf-8")
    con.execute(render_sql(texto, CohortParams(min_age=18)))

def test_concept_test_incluye_descendientes(con):
    correr_sql(con, "01_concept_sets.sql")
    ids= {r[0] for r in con.execute("SELECT concept_id FROM cs_epilepsia").fetchall()}
    assert ids == {1000, 1001}

def test_concept_test_antiepilepticos_excluye_otros_farmacos(con):
    correr_sql(con, "01_concept_sets.sql")
    ids= {r[0]for r in con.execute("SELECT concept_id FROM cs_antiepilepticos").fetchall()}
    assert ids == {2001, 2002}

def test_paso_1_personas_con_epilepsia(con):
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    personas = {r[0]for r in con.execute("SELECT person_id FROM cohort_step1").fetchall()}

def test_paso1_fecha_ìndice_es_el_primer_diagnostico(con):
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    fecha, n_dx = con.execute(
        "SELECT index_date, n_dx FROM cohort_step1 WHERE person_id = 1"
    ).fetchone()
    assert str(fecha) == "2020-06-01"
    assert n_dx == 2

def test_paso2_solo_adultos(con):
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    personas= {r[0]for r in con.execute ("SELECT person_id FROM cohort_step2").fetchall()}
    assert personas == {1,3,4,6,7}

def test_paso2_edad_en_la_fecha_indice(con):
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    edad= con.execute("SELECT age_at_index FROM cohort_step2 WHERE person_id =1").fetchone()[0]
    assert edad == 40

def test_paso2_frontera_mayoría_de_edad(con):
    con.execute("""
        INSERT INTO person VALUES (8, 8532, 2002, 6, 2), (9, 8532, 2002, 6, 1);
        INSERT INTO condition_occurrence VALUES (8, 1000, '2020-06-01'), (9, 1000, '2020-06-01');
    """)
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    personas= {r[0] for r in con.execute ("SELECT person_id FROM cohort_step2").fetchall()}
    assert 8 not in personas
    assert 9 in personas

def test_paso3_observacion_previa(con):
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con,"02_cohorte.sql")
    personas= {r[0] for r in con.execute ("SELECT person_id FROM cohort_step3").fetchall()}
    assert personas == {1,4,6,7}

def test_paso3_frontera_de_365_días(con):
    con.execute("""
        INSERT INTO person VALUES (10, 8532, 1990, 1, 1), (11, 8532, 1990, 1, 1), (12, 8532, 1990, 1, 1);
        INSERT INTO condition_occurrence VALUES
          (10, 1000, '2020-06-01'), (11, 1000, '2020-06-01'), (12, 1000, '2020-06-01');
        INSERT INTO observation_period VALUES
          (10, '2019-06-02', '2024-12-31'),
          (11, '2019-06-03', '2024-12-31'),
          (12, '2018-01-01', '2020-05-31');
    """)
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con,"02_cohorte.sql")
    personas={r[0] for r in con.execute ("SELECT person_id FROM cohort_step3").fetchall()}
    assert 10 in personas 
    assert 11 not in personas
    assert 12 not in personas

def test_paso4_con_antiepileptico(con):
        correr_sql(con, "01_concept_sets.sql")
        correr_sql(con,"02_cohorte.sql")
        personas= {r[0] for r in con.execute("SELECT person_id FROM cohort_step4").fetchall()}
        assert personas == {1,6,7}

def test_paso4_frontera_de_la_ventana_del_farmaco(con):
    con.execute("""
        INSERT INTO person VALUES
          (13, 8532, 1990, 1, 1), (14, 8532, 1990, 1, 1),
          (15, 8532, 1990, 1, 1), (16, 8532, 1990, 1, 1);
        INSERT INTO condition_occurrence VALUES
          (13, 1000, '2020-06-01'), (14, 1000, '2020-06-01'),
          (15, 1000, '2020-06-01'), (16, 1000, '2020-06-01');
        INSERT INTO observation_period VALUES
          (13, '2018-01-01', '2024-12-31'), (14, '2018-01-01', '2024-12-31'),
          (15, '2018-01-01', '2024-12-31'), (16, '2018-01-01', '2024-12-31');
        INSERT INTO drug_era VALUES
          (13, 2001, '2020-05-31'), (14, 2001, '2020-06-01'),
          (15, 2001, '2021-06-01'), (16, 2001, '2021-06-02');
    """)
    correr_sql(con,"01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    personas= {r[0]for r in con.execute("SELECT person_id FROM cohort_step4").fetchall()}
    assert 13 not in personas
    assert 14 in personas
    assert 15 in personas
    assert 16 not in personas

def test_tabla_cohorte_final(con):
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    personas= {r[0] for r in con.execute("SELECT person_id FROM cohort").fetchall()}
    assert personas == {1,6,7}

def cohorte_edad_y_sexo(con):
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    edad,sexo = con.execute (
        "SELECT age_at_index, sex FROM cohort WHERE person_id = 1"
    ).fetchone()
    assert edad == 40
    assert sexo == "F"

def tabla_de_atricion(con):
    correr_sql(con, "01_concept_sets.sql")
    correr_sql(con, "02_cohorte.sql")
    filas= con.execute ("SELECT n_persons, n_excluded FROM atrittion ORDER BY step").fetchall()
    assert [f[0] for f in filas] == [7, 6, 5, 4, 3]
    assert [f[1] for f in filas] == [0, 1, 1, 1, 1]

def test_render_sql_sustituye_todo():
    sql = render_sql("{{min_dx}} {{min_age}} {{prior_days}} {{followup_days}}", CohortParams())
    assert sql == "1 0 365 365"


def test_render_sql_rechaza_parametros_no_enteros():
    with pytest.raises(TypeError):
        render_sql("{{min_dx}}", CohortParams(min_dx="1; DROP TABLE person"))


def test_render_sql_avisa_si_queda_un_marcador():
    with pytest.raises(ValueError):
        render_sql("{{no_existe}}", CohortParams())


def test_por_defecto_entran_todas_las_edades(con):
    atricion = build_cohort(con)
    assert atricion.n_persons.tolist() == [7, 6, 6, 5, 4]
    personas = {r[0] for r in con.execute("SELECT person_id FROM cohort").fetchall()}
    assert personas == {1, 2, 6, 7}


def test_solo_adultos_con_min_age_18(con):
    atricion = build_cohort(con, CohortParams(min_age=18))
    assert atricion.n_persons.tolist() == [7, 6, 5, 4, 3]
    personas = {r[0] for r in con.execute("SELECT person_id FROM cohort").fetchall()}
    assert personas == {1, 6, 7}


def test_un_bebe_queda_fuera_por_la_observacion_previa(con):
    # Persona 8: nace 2019-12-01, su observación empieza al nacer y se le diagnostica a los 6 meses.
    con.execute("""
        INSERT INTO person VALUES (8, 8532, 2019, 12, 1);
        INSERT INTO condition_occurrence VALUES (8, 1000, '2020-06-01');
        INSERT INTO observation_period VALUES (8, '2019-12-01', '2024-12-31');
        INSERT INTO drug_era VALUES (8, 2001, '2020-06-15');
    """)
    build_cohort(con)  # con 365 días de observación previa
    assert 8 not in {r[0] for r in con.execute("SELECT person_id FROM cohort").fetchall()}
    build_cohort(con, CohortParams(prior_days=0))
    assert 8 in {r[0] for r in con.execute("SELECT person_id FROM cohort").fetchall()}


def test_min_dx_2_deja_fuera_a_quien_tiene_un_solo_diagnostico(con):
    build_cohort(con, CohortParams(min_dx=2))
    personas = {r[0] for r in con.execute("SELECT person_id FROM cohort").fetchall()}
    assert personas == {1, 6}


def test_min_age_40_incluye_a_quien_tiene_exactamente_40(con):
    atricion = build_cohort(con, CohortParams(min_age=40))
    personas = {r[0] for r in con.execute("SELECT person_id FROM cohort").fetchall()}
    assert personas == {1, 7}
    assert "40" in atricion.description[2]