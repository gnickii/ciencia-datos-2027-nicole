import duckdb
import pandas as pd
import pytest
from conftest import DATOS, SCHEMA

from epilepsia_omop.cli import VARIANTES, main
from epilepsia_omop.db import connect


@pytest.fixture
def base_en_disco(tmp_path):
    """La misma base de juguete, pero guardada en un archivo .duckdb real."""
    ruta = tmp_path / "juguete.duckdb"
    con = duckdb.connect(str(ruta))
    con.execute(SCHEMA)
    con.execute(DATOS)
    con.close()
    return ruta


def test_connect_falla_con_mensaje_claro_si_no_hay_base(tmp_path):
    with pytest.raises(FileNotFoundError, match="--db"):
        connect(tmp_path / "no_existe.duckdb")


def test_variante_principal_escribe_los_csv(base_en_disco, tmp_path):
    out = tmp_path / "salida"
    main(["--db", str(base_en_disco), "--out", str(out)])
    carpeta = out / "principal"
    for archivo in ("attrition", "table1_sexo", "table1_edad", "primer_aed"):
        assert (carpeta / f"{archivo}.csv").exists()
    atricion = pd.read_csv(carpeta / "attrition.csv")
    assert atricion["n_persons"].tolist() == [7, 6, 6, 5, 4]


def test_todas_las_variantes_generan_su_carpeta(base_en_disco, tmp_path):
    out = tmp_path / "salida"
    main(["--db", str(base_en_disco), "--out", str(out), "--variante", "todas"])
    for nombre in VARIANTES:
        assert (out / nombre / "attrition.csv").exists()


def test_solo_adultos_tiene_menos_gente_que_el_principal(base_en_disco, tmp_path):
    out = tmp_path / "salida"
    main(["--db", str(base_en_disco), "--out", str(out), "--variante", "todas"])
    principal = pd.read_csv(out / "principal" / "attrition.csv")["n_persons"].iloc[-1]
    adultos = pd.read_csv(out / "solo_adultos" / "attrition.csv")["n_persons"].iloc[-1]
    assert adultos == principal - 1  # se va la persona 2, nacida en 2015