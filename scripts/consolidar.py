# consolidar.py
from pathlib import Path
import pandas as pd  # pandas: librería para trabajar con tablas de datos

def consolidar(carpeta, salida="consolidado.xlsx"):
    tablas = []
    for archivo in Path(carpeta).glob("*.xlsx"):   # glob: busca archivos por patrón
        df = pd.read_excel(archivo)                # df = tabla (DataFrame)
        df["origen"] = archivo.name                # columna extra: de qué archivo vino
        tablas.append(df)

    if not tablas:
        print("❌ No se encontraron archivos .xlsx")
        return

    total = pd.concat(tablas, ignore_index=True)   # une todas las tablas en una
    total.to_excel(salida, index=False)
    print(f"✅ {len(tablas)} archivos unidos → {salida} ({len(total)} filas)")

if __name__ == "__main__":
    consolidar("./reportes")
