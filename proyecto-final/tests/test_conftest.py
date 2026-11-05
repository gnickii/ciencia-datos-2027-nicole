def test_base_tiene_siete_pacientes(con):
     assert con.execute("SELECT count(*) FROM person").fetchone()[0] == 7
     
        