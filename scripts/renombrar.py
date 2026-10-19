# renombrar.py
from pathlib import Path  # Path: forma moderna de trabajar con rutas de archivos
import argparse           # argparse: lee opciones escritas en la terminal
import re                 # re: busca patrones en los nombres de archivo

# Archivos del sistema o del editor que no hay que renombrar nunca.
# OJO: Thumbs.db y desktop.ini NO empiezan con punto, por eso van aparte.
OCULTOS = {".ds_store", "thumbs.db", "desktop.ini"}

def renombrar(carpeta, prefijo, simular):
    ruta = Path(carpeta)

    # Validamos que la carpeta exista (programación defensiva)
    if not ruta.is_dir():
        print(f"❌ La carpeta '{carpeta}' no existe.")
        return

    # sorted() para que el orden sea siempre el mismo
    # Los ocultos (.gitkeep, .DS_Store) y los del sistema (Thumbs.db) se ignoran
    archivos = sorted(
        f for f in ruta.iterdir()
        if f.is_file()
        and not f.name.startswith(".")
        and f.name.lower() not in OCULTOS
    )

    # Patrón del nombre final: producto_001.jpg  (prefijo + _ + 3 dígitos + extensión)
    patron = re.compile(rf"^{re.escape(prefijo)}_(\d{{3}})(\.[^.]+)?$")

    ya_renombrados = []   # (archivo, número que ya tiene)
    a_renombrar = []      # archivos que todavía hay que renombrar
    for f in archivos:
        m = patron.match(f.name)
        if m:
            ya_renombrados.append((f, int(m.group(1))))
        else:
            a_renombrar.append(f)

    # Los archivos ya renombrados se respetan: el siguiente número es el mayor usado + 1
    siguiente = max((n for _, n in ya_renombrados), default=0) + 1

    renombrados = 0
    saltados = len(ya_renombrados)
    errores = 0

    for archivo, _ in ya_renombrados:
        print(f"➖ Sin cambios (ya tiene el nombre correcto): {archivo.name}")

    for archivo in a_renombrar:
        # Extensión siempre en minúsculas: .JPG -> .jpg
        extension = archivo.suffix.lower()

        # Busco el primer número libre para no pisar ningún archivo
        while True:
            nuevo_nombre = f"{prefijo}_{siguiente:03d}{extension}"
            destino = ruta / nuevo_nombre
            siguiente += 1
            if not destino.exists():
                break

        print(f"{archivo.name}  →  {nuevo_nombre}")
        if not simular:           # Solo renombra si NO es simulación
            try:
                archivo.rename(destino)
            except OSError as e:  # OSError: errores de archivos o permisos
                print(f"❌ No se pudo renombrar {archivo.name}: {e}")
                errores += 1
                continue            # sigue con el próximo archivo
        renombrados += 1            # fuera del if: en simulación cuenta lo que haría

    # Resumen final
    if simular:
        print(f"\n🔎 Simulación: se renombrarían {renombrados} archivos, "
              f"{saltados} ya estaban bien. No se cambió nada.")
    else:
        extra = f", {errores} errores" if errores else ""
        print(f"\n✅ {renombrados} archivos renombrados, {saltados} saltados{extra}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Renombra archivos en masa")
    parser.add_argument("carpeta", help="Carpeta con los archivos")
    parser.add_argument("--prefijo", default="archivo", help="Prefijo del nuevo nombre")
    parser.add_argument("--simular", action="store_true", help="Solo mostrar, no renombrar")
    args = parser.parse_args()

    renombrar(args.carpeta, args.prefijo, args.simular)
