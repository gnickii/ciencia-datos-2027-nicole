from pathlib import Path 

SQL_DIR= Path (__file__).resolve().parents[1]/"sql"

def correr_sql(con, nombre):
    """Lee un archivo sql y lo corre"""
    texto= (SQL_DIR/nombre).read_text(encoding="utf-8")
    con.execute(texto)

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