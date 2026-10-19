# renombrar.py
from pathlib import Path  # Path: forma moderna de trabajar con rutas de archivos
import argparse           # argparse: lee opciones escritas en la terminal
import re                 # re: busca patrones en los nombres de archivo

def renombrar(carpeta, prefijo, simular):
    ruta = Path(carpeta)

    # Validamos que la carpeta exista (programación defensiva)
    if not ruta.is_dir():
        print(f"❌ La carpeta '{carpeta}' no existe.")
        return

    # sorted() para que el orden sea siempre el mismo
    archivos = sorted(f for f in ruta.iterdir() if f.is_file())

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
            archivo.rename(destino)
        renombrados += 1

    # Resumen final
    if simular:
        print(f"\n🔎 Simulación: {renombrados} archivos renombrados, {saltados} saltados. No se cambió nada.")
    else:
        print(f"\n✅ {renombrados} archivos renombrados, {saltados} saltados.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Renombra archivos en masa")
    parser.add_argument("carpeta", help="Carpeta con los archivos")
    parser.add_argument("--prefijo", default="archivo", help="Prefijo del nuevo nombre")
    parser.add_argument("--simular", action="store_true", help="Solo mostrar, no renombrar")
    args = parser.parse_args()

    renombrar(args.carpeta, args.prefijo, args.simular)
