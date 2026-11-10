from epilepsia_omop.characterize import characterize
from epilepsia_omop.cohort import CohortParams


def test_tabla_por_sexo(con):
    tablas= characterize(con)
    sexo= dict(zip(tablas["table1_sexo"]["sex"], tablas ["table1_sexo"]["n"]))
    assert sum(sexo.values()) == 4 
    assert tablas ["table1_sexo"]["pct"].sum() == 100.0


def test_grupos_de_edad_suman_la_cohorte(con):
    tablas= characterize(con)
    assert tablas["table1_edad"]["n"].sum() == 4


def test_paciente_menor_de_18(con):
    tablas= characterize(con)
    edad=dict(zip(tablas["table1_edad"]["grupo_edad"], tablas["table1_edad"]["n"]))
    assert edad["0-17"] == 1 


def test_un_bebe_cae_en_grupo_0_17(con):
    con.execute("""
        INSERT INTO person VALUES (8, 8532, 2019, 12, 1);
        INSERT INTO condition_occurrence VALUES (8, 1000, '2020-06-01');
        INSERT INTO observation_period VALUES (8, '2019-12-01', '2024-12-31');
        INSERT INTO drug_era VALUES (8, 2001, '2020-06-15');
    """)
    tablas= characterize(con,CohortParams(prior_days=0))
    edad= dict(zip(tablas["table1_edad"]["grupo_edad"],tablas["table1_edad"]["n"]))
    assert edad['0-17'] == 2 


def test_primer_antiepileptico(con):
    tablas=characterize(con)
    aed= dict(zip(tablas["primer_aed"]["medicamento"],tablas["primer_aed"]["n"]))
    assert aed == {"Levetiracetam":3, "Lamotrigine":1}