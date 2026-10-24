# consolidar.py
from pathlib import Path
import argparse
from datetime import date, datetime

import pandas as pd


def normalizar_fecha(valor, formato_local="%d/%m/%Y"):
    """Convierte lo que venga en una fecha real.

    - Fecha ya real (openpyxl suele mandar datetime.date/datetime): se respeta tal cual.
    - Texto: primero ISO (2026-01-05), después el formato local del cliente,
      si no se puede interpretar, queda vacía (NaT) y el script avisa.
    """
    if pd.isna(valor):                                     # None, NaN, NaT
        return pd.NaT
    if isinstance(valor, (pd.Timestamp, datetime, date)):   # ya es fecha real
        return pd.Timestamp(valor)
    texto = str(valor).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", formato_local):
        try:
            return pd.to_datetime(texto, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT                                          # no se pudo interpretar


def elegir_formato(serie, eleccion):
    """Formato local a usar según --formato-fecha.

    En 'auto' decide UNA VEZ por columna: si algún valor tiene un componente
    mayor a 12, eso define de qué lado está el día. Si nada lo define, se usa
    día/mes y el script avisa que fue una decisión nuestra.
    """
    if eleccion == "mes":
        return "%m/%d/%Y", "definido"
    if eleccion == "dia":
        return "%d/%m/%Y", "definido"

    hay_dia = hay_mes = False
    hay_texto = False
    for valor in serie:
        if pd.isna(valor) or isinstance(valor, (date, datetime)):
            continue                          # no aporta para definir el formato
        partes = str(valor).strip().split("/")
        if len(partes) != 3:
            continue
        try:
            primero, segundo = int(partes[0]), int(partes[1])
        except ValueError:
            continue
        hay_texto = True
        if primero > 12:
            hay_dia = True
        if segundo > 12:
            hay_mes = True

    if not hay_texto:
        return "%Y-%m-%d", "ya_fechas"        # la columna ya venía como fecha real
    if hay_dia and not hay_mes:
        return "%d/%m/%Y", "definido"
    if hay_mes and not hay_dia:
        return "%m/%d/%Y", "definido"
    return "%d/%m/%Y", "ambiguo"


def armar_resumen(total, hojas_omitidas, archivos_fallidos, hojas_distintas):
    """Tabla de dos columnas (Indicador, Valor) para el cliente.

    Todos los números salen de `total` (los datos reales), salvo los contadores
    de omisiones: así el resumen nunca puede contradecir a los datos.
    """
    datos = {
        "Filas consolidadas": len(total),
        "Archivos con datos": total["origen"].nunique(),
        "Hojas unidas": total.groupby(["origen", "hoja"]).ngroups,
        "Hojas omitidas (vacías)": hojas_omitidas,
        "Archivos ilegibles": archivos_fallidos,
        "Hojas con columnas distintas": hojas_distintas,
        "Filas con celdas vacías": int(total.isna().any(axis=1).sum()),
    }

    # Celdas vacías por columna
    vacios = total.isna().sum()
    for col, n in vacios[vacios > 0].items():
        datos[f"Celdas vacías en '{col}'"] = int(n)

    # Rango de fechas: solo si la columna ya es de tipo fecha.
    # Con fechas en texto el orden alfabético no es el orden real, así que
    # mejor no mostrar un rango que podría ser falso.
    if "fecha" in total.columns and pd.api.types.is_datetime64_any_dtype(total["fecha"]):
        fechas = total["fecha"].dropna()
        if not fechas.empty:
            # strftime para que el resumen muestre la fecha, no la fecha con la hora
            datos["Fecha más antigua"] = fechas.min().strftime("%Y-%m-%d")
            datos["Fecha más reciente"] = fechas.max().strftime("%Y-%m-%d")
        else:
            datos["Rango de fechas"] = "sin fechas"

    # Todo como texto: en una misma columna, Excel muestra mejor los valores iguales
    return pd.DataFrame(
        [(k, str(v)) for k, v in datos.items()],
        columns=["Indicador", "Valor"],
    )


def consolidar(carpeta, salida, simular=False, formato_fecha="dia", fila_encabezado=1):
    ruta = Path(carpeta)
    if not ruta.is_dir():
        print(f"❌ La carpeta '{carpeta}' no existe.")
        return

    if fila_encabezado < 1:
        print("❌ --fila-encabezado tiene que ser 1 o más (1 = primera fila del Excel).")
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
            # header=fila_encabezado-1: los reports de clientes suelen tener
            # títulos arriba de los encabezados; esto los salta.
            hojas = pd.read_excel(archivo, sheet_name=None, header=fila_encabezado - 1)
        except Exception as e:
            # Mensaje para el cliente + el nombre del error, por si hay que pedir ayuda
            print(f"❌ No se pudo leer {archivo.name}: "
                  f"¿está dañado o no es un Excel real? ({type(e).__name__})")
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

    # Normalización de fechas: de texto a fecha real
    if "fecha" in total.columns and total["fecha"].notna().any():
        formato_local, tipo = elegir_formato(total["fecha"], formato_fecha)
        if tipo == "ya_fechas":
            # openpyxl ya trajo fechas correctas: solo garantizamos el tipo
            total["fecha"] = pd.to_datetime(total["fecha"])
            print("ℹ️  La columna 'fecha' ya venía como fecha real de Excel.")
        else:
            original = total["fecha"]
            total["fecha"] = pd.to_datetime(
                original.apply(lambda v: normalizar_fecha(v, formato_local))
            )
            # Solo cuentan las que tenían contenido y quedaron vacías
            malas = int(original.notna().sum() - total["fecha"].notna().sum())
            if tipo == "ambiguo":
                print(f"⚠️  Fechas ambiguas: se interpretaron como DD/MM/AAAA. "
                      f"Si viene al revés, usá --formato-fecha mes.")
            if malas:
                print(f"⚠️  {malas} fecha(s) no se pudieron interpretar (quedan vacías).")
            if original.notna().any():
                print(f"ℹ️  Columna 'fecha' normalizada a fecha real ({formato_local}).")

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
        print("\nHoja 'Resumen' que se generaría:")
        print(armar_resumen(total, hojas_omitidas, archivos_fallidos, hojas_distintas)
              .to_string(index=False))
        return

    # Dos hojas: 'Resumen' primero (es lo primero que mira el cliente) y 'Datos'.
    # date_format para que Excel muestre 2026-01-05 y no 2026-01-05 00:00:00
    resumen = armar_resumen(total, hojas_omitidas, archivos_fallidos, hojas_distintas)
    with pd.ExcelWriter(salida, date_format="YYYY-MM-DD") as w:
        resumen.to_excel(w, sheet_name="Resumen", index=False)
        total.to_excel(w, sheet_name="Datos", index=False)
    print(f"\n✅ {len(tablas)} hojas unidas → {salida} ({len(total)} filas)")
    print("\nHoja 'Resumen' del archivo generado:")
    print(resumen.to_string(index=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Une varios Excel en uno solo")
    parser.add_argument("carpeta", help="Carpeta con los .xlsx")
    parser.add_argument("--salida", default="consolidado.xlsx", help="Nombre del archivo final")
    parser.add_argument("--simular", action="store_true", help="Solo mostrar, no escribir el Excel")
    parser.add_argument("--formato-fecha", choices=["dia", "mes", "auto"], default="dia",
                        help="Cómo interpretar fechas tipo 05/02/2026: día/mes (LatAm) o "
                             "mes/día (EE. UU.). 'auto' deduce una vez por columna.")
    parser.add_argument("--fila-encabezado", type=int, default=1,
                        help="Fila donde están los encabezados, por si el reporte tiene "
                             "títulos arriba (ej: 3 = tercera fila). Por defecto 1.")
    args = parser.parse_args()
    consolidar(args.carpeta, args.salida, args.simular, args.formato_fecha,
               args.fila_encabezado)
