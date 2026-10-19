# Automatizaciones con Python

Colección de scripts para automatizar tareas repetitivas:

1. Renombrar archivos en masa
2. Consolidar varios Excel en uno solo
3. Enviar emails personalizados desde una lista

> 🚧 Proyecto en desarrollo.

## Ejemplo rápido

```bash
# 1. Simulación: ver qué haría SIN tocar nada (empezá siempre así)
python3 scripts/renombrar.py datos_prueba/fotos --prefijo producto --simular

# 2. Renombrar de verdad
python3 scripts/renombrar.py datos_prueba/fotos --prefijo producto

# 3. Renombrar solo algunos tipos de archivo
python3 scripts/renombrar.py datos_prueba/fotos --prefijo producto --extensiones jpg,png
```

## Requisitos

- Python 3.14 (versión usada en este proyecto, compatible con 3.10+).
- Usá `python3` en Linux/Mac y `python` en Windows si `python3` no te funciona. Ambos deben apuntar a Python 3.14.

## Seguridad

- Modo simulación antes de tocar nada.
- No pisa archivos existentes.
- Se puede correr varias veces sin romper nada.
- Ignora archivos de sistema (.DS_Store, Thumbs.db) y maneja errores sin frenarse.
- Permite elegir qué tipos de archivo renombrar.

## Instalación

    python -m venv venv
    source venv/bin/activate    # En Windows: venv\Scripts\activate
    pip install -r requirements.txt

## Uso

### 1. Renombrar archivos en masa

Opciones:

- `--prefijo`: prefijo del nombre nuevo (por defecto `archivo`).
- `--simular`: solo muestra lo que haría, no renombra nada.
- `--extensiones`: renombra solo esos tipos, separados por coma (ej: `jpg,png`).

Resultado:

```text
IMG_4521.jpg  →  producto_001.jpg
documento final.PDF  →  producto_002.pdf

✅ 20 archivos renombrados, 0 saltados.
```

Nombres del estilo `producto_001.jpg`, con la extensión siempre en minúsculas.
Los archivos ocultos (`.gitkeep`, `.DS_Store`) y los del sistema (`Thumbs.db`)
se ignoran, y el script avisa si algún archivo no se pudo renombrar.
