import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
LIMITE_MB = 5
PROHIBIDOS = (".duckdb", ".db", ".wal")

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git no está instalado")


def archivos_rastreados():
    """Lista de archivos que git está versionando dentro de proyecto-final/."""
    salida = subprocess.run(
        ["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True, check=True
    ).stdout
    return [RAIZ / linea for linea in salida.splitlines() if linea]


def test_gitignore_cubre_lo_esencial():
    texto = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    for patron in (".venv/", "__pycache__/", "data/*.duckdb"):
        assert patron in texto, f"Falta {patron} en .gitignore"


def test_no_hay_bases_de_datos_en_git():
    malos = [p.name for p in archivos_rastreados() if p.suffix in PROHIBIDOS]
    assert malos == [], f"Archivos de base de datos versionados: {malos}"


def test_no_hay_archivos_grandes_en_git():
    grandes = [
        p.name
        for p in archivos_rastreados()
        if p.exists() and p.stat().st_size > LIMITE_MB * 1024 * 1024
    ]
    assert grandes == [], f"Archivos de más de {LIMITE_MB} MB versionados: {grandes}"