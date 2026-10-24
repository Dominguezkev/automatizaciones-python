# tests/test_fechas.py
"""Tests de normalizar_fecha: distintos tipos de dato que pueden llegar de Excel.

Correrlos:
    ./venv/bin/python tests/test_fechas.py

También funcionan con pytest, si un día lo instalamos:
    ./venv/bin/python -m pytest tests/
"""
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

# Permite ejecutar este archivo desde cualquier carpeta
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.consolidar import normalizar_fecha   # noqa: E402


def test_fecha_iso():
    assert normalizar_fecha("2026-01-05") == pd.Timestamp("2026-01-05")


def test_fecha_local_dia_primero():
    # 05/02/2026 = 5 de febrero (LatAm), NO 2 de mayo
    assert normalizar_fecha("05/02/2026") == pd.Timestamp("2026-02-05")


def test_fecha_local_mes_primero():
    # Cliente de EE. UU.: 05/02/2026 = 2 de mayo
    assert normalizar_fecha("05/02/2026", formato_local="%m/%d/%Y") == pd.Timestamp("2026-05-02")


def test_texto_con_hora():
    # Excel a veces entrega el ISO con la hora: 2026-01-05 00:00:00
    assert normalizar_fecha("2026-01-05 00:00:00") == pd.Timestamp("2026-01-05")


def test_basura_devuelve_nat():
    assert pd.isna(normalizar_fecha("basura"))


def test_date_de_python():
    # openpyxl entrega datetime.date cuando la celda ES una fecha de verdad
    assert normalizar_fecha(date(2026, 1, 5)) == pd.Timestamp("2026-01-05")


def test_datetime_de_python():
    assert normalizar_fecha(datetime(2026, 1, 5, 12, 30)) == pd.Timestamp("2026-01-05 12:30:00")


def test_none_devuelve_nat():
    # Celda vacía: la función no se rompe, devuelve vacío
    assert pd.isna(normalizar_fecha(None))


if __name__ == "__main__":
    pruebas = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    ok = 0
    for prueba in pruebas:
        try:
            prueba()
            ok += 1
            print(f"✔ {prueba.__name__}")
        except AssertionError as e:
            print(f"❌ FALLÓ: {prueba.__name__} ({e})")
    print(f"\n{'✅' if ok == len(pruebas) else '❌'} {ok} de {len(pruebas)} tests OK")
    sys.exit(0 if ok == len(pruebas) else 1)
