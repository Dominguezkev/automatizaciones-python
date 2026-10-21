# generar_excels_prueba.py: crea Excel "sucios" para probar consolidar.py
from pathlib import Path
import pandas as pd

carpeta = Path("datos_prueba/reportes")
carpeta.mkdir(parents=True, exist_ok=True)

# 1. Archivo normal
pd.DataFrame({
    "fecha": ["2026-01-05", "2026-01-12"],
    "producto": ["Camisa", "Pantalón"],
    "monto": [15000, 22000],
}).to_excel(carpeta / "ventas_enero.xlsx", index=False)

# 2. Columnas distintas (falta 'monto', sobra 'vendedor')
pd.DataFrame({
    "fecha": ["05/02/2026", "10/02/2026"],
    "producto": ["Zapatos", "Medias"],
    "vendedor": ["Ana", "Luis"],
}).to_excel(carpeta / "ventas_febrero.xlsx", index=False)

# 3. Dos hojas: Marzo con datos, Abril vacía
with pd.ExcelWriter(carpeta / "ventas_marzo_abril.xlsx") as w:
    pd.DataFrame({
        "fecha": ["2026-03-03"], "producto": ["Campera"], "monto": [48000],
    }).to_excel(w, sheet_name="Marzo", index=False)
    pd.DataFrame().to_excel(w, sheet_name="Abril", index=False)

# 4. Archivo sin datos (solo encabezados)
pd.DataFrame(columns=["fecha", "producto", "monto"]).to_excel(
    carpeta / "ventas_vacio.xlsx", index=False
)

print(f"✅ Excel de prueba creados en {carpeta}")
