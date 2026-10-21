# consolidar.py
from pathlib import Path
import argparse
import pandas as pd

def consolidar(carpeta, salida):
    ruta = Path(carpeta)
    if not ruta.is_dir():
        print(f"❌ La carpeta '{carpeta}' no existe.")
        return

    # Ignoramos archivos temporales de Excel (~$...) y el propio archivo de salida
    archivos = sorted(
        f for f in ruta.glob("*.xlsx")
        if not f.name.startswith("~$") and f.name != Path(salida).name
    )
    if not archivos:
        print("❌ No se encontraron archivos .xlsx")
        return

    tablas = []
    columnas_vistas = None   # para avisar si hay columnas distintas

    for archivo in archivos:
        try:
            # sheet_name=None -> lee TODAS las hojas (devuelve un dict nombre -> tabla)
            hojas = pd.read_excel(archivo, sheet_name=None)
        except Exception as e:
            print(f"❌ No se pudo leer {archivo.name}: {e}")
            continue

        for nombre_hoja, df in hojas.items():
            if df.empty:
                print(f"➖ Hoja vacía, se omite: {archivo.name} / {nombre_hoja}")
                continue

            df["origen"] = archivo.name      # de qué archivo vino
            df["hoja"] = nombre_hoja         # de qué hoja vino

            # Aviso si las columnas no coinciden con el primer archivo válido
            cols = set(df.columns) - {"origen", "hoja"}
            if columnas_vistas is None:
                columnas_vistas = cols
            elif cols != columnas_vistas:
                print(f"⚠️  Columnas distintas en {archivo.name} / {nombre_hoja}: "
                      f"{sorted(cols ^ columnas_vistas)}")

            tablas.append(df)
            print(f"✔ {archivo.name} / {nombre_hoja}: {len(df)} filas")

    if not tablas:
        print("❌ No hubo datos para consolidar.")
        return

    total = pd.concat(tablas, ignore_index=True)
    total.to_excel(salida, index=False)
    print(f"\n✅ {len(tablas)} hojas unidas → {salida} ({len(total)} filas)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Une varios Excel en uno solo")
    parser.add_argument("carpeta", help="Carpeta con los .xlsx")
    parser.add_argument("--salida", default="consolidado.xlsx", help="Nombre del archivo final")
    args = parser.parse_args()
    consolidar(args.carpeta, args.salida)
