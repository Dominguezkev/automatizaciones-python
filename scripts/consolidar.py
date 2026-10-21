# consolidar.py
from pathlib import Path
import argparse
import pandas as pd

def consolidar(carpeta, salida, simular=False):
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
    hojas_omitidas = 0       # hojas vacías que se dejaron afuera
    archivos_fallidos = 0    # archivos que no se pudieron leer
    hojas_distintas = 0      # hojas con columnas que no coinciden

    for archivo in archivos:
        try:
            # sheet_name=None -> lee TODAS las hojas (devuelve un dict nombre -> tabla)
            hojas = pd.read_excel(archivo, sheet_name=None)
        except Exception as e:
            print(f"❌ No se pudo leer {archivo.name}: {e}")
            archivos_fallidos += 1
            continue

        for nombre_hoja, df in hojas.items():
            if df.empty:
                print(f"➖ Hoja vacía, se omite: {archivo.name} / {nombre_hoja}")
                hojas_omitidas += 1
                continue

            df["origen"] = archivo.name      # de qué archivo vino
            df["hoja"] = nombre_hoja         # de qué hoja vino

            # Aviso si las columnas no coinciden con el primer archivo válido
            cols = set(df.columns) - {"origen", "hoja"}
            if columnas_vistas is None:
                columnas_vistas = cols
            elif cols != columnas_vistas:
                hojas_distintas += 1
                faltan = sorted(columnas_vistas - cols)
                sobran = sorted(cols - columnas_vistas)
                print(f"⚠️  Columnas distintas en {archivo.name} / {nombre_hoja}: "
                      f"faltan {faltan}, sobran {sobran}. "
                      f"Las {len(df)} filas quedan con celdas vacías.")

            tablas.append(df)
            print(f"✔ {archivo.name} / {nombre_hoja}: {len(df)} filas")

    if not tablas:
        print("❌ No hubo datos para consolidar.")
        return

    total = pd.concat(tablas, ignore_index=True)

    # Nada se pierde en silencio: avisamos cuántas filas quedan con celdas vacías
    incompletas = int(total.isna().any(axis=1).sum())
    if incompletas:
        vacios = total.isna().sum()
        detalle = ", ".join(f"{col}: {n}" for col, n in vacios[vacios > 0].items())
        print(f"⚠️  {incompletas} de {len(total)} filas quedan con celdas vacías ({detalle}).")

    # Detalle de lo que quedó afuera
    omitidos = []
    if hojas_omitidas:
        omitidos.append(f"{hojas_omitidas} hoja(s) vacía(s)")
    if archivos_fallidos:
        omitidos.append(f"{archivos_fallidos} archivo(s) ilegible(s)")
    if hojas_distintas:
        omitidos.append(f"{hojas_distintas} hoja(s) con columnas distintas")
    if omitidos:
        print("➖ Omitido del resultado: " + " · ".join(omitidos))

    if simular:
        print(f"\n🔎 Simulación: se unirían {len(tablas)} hojas ({len(total)} filas) "
              f"→ {salida}. No se escribió nada.")
        return

    total.to_excel(salida, index=False)
    print(f"\n✅ {len(tablas)} hojas unidas → {salida} ({len(total)} filas)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Une varios Excel en uno solo")
    parser.add_argument("carpeta", help="Carpeta con los .xlsx")
    parser.add_argument("--salida", default="consolidado.xlsx", help="Nombre del archivo final")
    parser.add_argument("--simular", action="store_true", help="Solo mostrar, no escribir el Excel")
    args = parser.parse_args()
    consolidar(args.carpeta, args.salida, args.simular)
