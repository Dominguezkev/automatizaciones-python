# renombrar.py
from pathlib import Path  # Path: forma moderna de trabajar con rutas de archivos
import argparse           # argparse: lee opciones escritas en la terminal

def renombrar(carpeta, prefijo, simular):
    ruta = Path(carpeta)

    # Validamos que la carpeta exista (programación defensiva)
    if not ruta.is_dir():
        print(f"❌ La carpeta '{carpeta}' no existe.")
        return

    # sorted() para que el orden sea siempre el mismo
    archivos = sorted(f for f in ruta.iterdir() if f.is_file())

    for i, archivo in enumerate(archivos, start=1):
        # suffix = extensión (.jpg, .pdf...). Se conserva igual.
        nuevo_nombre = f"{prefijo}_{i:03d}{archivo.suffix}"  # :03d -> 001, 002...
        destino = ruta / nuevo_nombre

        if destino.exists():
            print(f"⚠️  Saltado (ya existe): {nuevo_nombre}")
            continue

        print(f"{archivo.name}  →  {nuevo_nombre}")
        if not simular:           # Solo renombra si NO es simulación
            archivo.rename(destino)

    if simular:
        print("\n🔎 Modo simulación: no se cambió nada. Quitá --simular para aplicar.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Renombra archivos en masa")
    parser.add_argument("carpeta", help="Carpeta con los archivos")
    parser.add_argument("--prefijo", default="archivo", help="Prefijo del nuevo nombre")
    parser.add_argument("--simular", action="store_true", help="Solo mostrar, no renombrar")
    args = parser.parse_args()

    renombrar(args.carpeta, args.prefijo, args.simular)
