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