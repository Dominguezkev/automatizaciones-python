# Automatizaciones con Python

Colección de scripts para automatizar tareas repetitivas:

1. Renombrar archivos en masa
2. Consolidar varios Excel en uno solo
3. Enviar emails personalizados desde una lista

> ✅ Los 3 scripts están terminados y listos para usar.

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

### 2. Consolidar varios Excel en uno

Une todas las hojas de todos los `.xlsx` de una carpeta en un solo archivo,
con una hoja `Resumen` que dice cuántos datos entraron y qué quedó afuera:

![Resumen del Excel consolidado](docs/resumen.png)

```bash
# 1. Simulación: ver qué uniría SIN escribir nada (empezá siempre así)
python3 scripts/consolidar.py datos_prueba/reportes --simular

# 2. Consolidar de verdad
python3 scripts/consolidar.py datos_prueba/reportes --salida consolidado.xlsx

# 3. Reporte de cliente con títulos arriba de los encabezados
python3 scripts/consolidar.py datos_prueba/cliente --salida consolidado.xlsx \
    --formato-fecha auto --fila-encabezado 3
```

Opciones:

- `--salida`: nombre del Excel final (por defecto `consolidado.xlsx`).
- `--simular`: solo muestra lo que haría, no escribe nada.
- `--formato-fecha dia|mes|auto`: cómo leer fechas tipo `05/02/2026`.
  `dia` = día/mes (LatAm), `mes` = mes/día (EE. UU.), `auto` lo deduce solo.
- `--fila-encabezado N`: fila donde están los encabezados, por si el reporte
  tiene títulos arriba (ej: `3` = tercera fila). Por defecto 1.

Qué hace el script:

- Lee **todas las hojas** de cada archivo, no solo la primera.
- Omite hojas vacías y avisos legibles si un archivo no se pudo leer:
  nada queda afuera en silencio.
- Avisa si una hoja tiene columnas distintas a las demás.
- Normaliza la columna `fecha`: acepta fechas reales de Excel y texto en
  varios formatos, y las deja como fecha de verdad en el resultado final.
- El Excel de salida trae dos hojas: `Resumen` (indicadores para el cliente)
  y `Datos` (todo el contenido unido, con columnas `origen` y `hoja`).

> 💡 Si el reporte tiene un título en la primera fila, pandas nombla las
> columnas `Unnamed: 1`, `Unnamed: 2`… El script entra igual pero **avisa**
> en pantalla para que uses `--fila-encabezado` con la fila que corresponda.

### 3. Enviar emails personalizados

Lee un CSV de contactos y una plantilla con `{columna}`, y envía un email
personalizado a cada contacto con email válido.

![Simulación de envío de emails](docs/envios.png)

Por defecto **solo simula**: muestra exactamente qué recibiría cada persona
y no manda nada. El envío de verdad pide confirmación antes de arrancar.

```bash
# 1. Simulación con los ejemplos del repo (copialos y adaptalos a tus datos)
python3 scripts/enviar_emails.py datos_prueba/contactos.ejemplo.csv \
    --plantilla datos_prueba/plantilla.ejemplo.txt

# 2. Envío de verdad: muestra el detalle, pide "(s/n)" y recién ahí envía
python3 scripts/enviar_emails.py datos_prueba/contactos.ejemplo.csv \
    --plantilla datos_prueba/plantilla.ejemplo.txt --enviar

# 3. Con tope: como mucho 3 emails hoy (cuenta los que ya mandaste hoy)
python3 scripts/enviar_emails.py datos_prueba/contactos.ejemplo.csv \
    --plantilla datos_prueba/plantilla.ejemplo.txt --max 3
```

Opciones:

- `--plantilla`: archivo con el texto, usando `{columna}` del CSV (por defecto `plantilla.txt`).
- `--asunto`: asunto del email (por defecto `Recordatorio`).
- `--max`: tope de envíos por día (por defecto 20); descuenta lo ya enviado
  hoy leyendo `envios.log`.
- `--enviar`: envía de verdad. Sin esto, solo simula.

#### Formato del CSV y de la plantilla

El CSV tiene una fila de encabezados y una fila por contacto; las columnas
extra no molestan:

```csv
nombre,email,turno
Ana,ana@ejemplo.com,jueves 15:30
```

La plantilla es texto con `{columna}` donde querés el dato del CSV:

```text
Hola {nombre}, te recordamos que tu turno es el {turno}.
```

En `datos_prueba/` hay versiones con datos falsos para copiar:
`contactos.ejemplo.csv` y `plantilla.ejemplo.txt`.

#### Configuración (solo la primera vez)

1. Activá la **verificación en dos pasos** en tu cuenta de Google
   (Cuenta de Google → Seguridad).
2. Creá una **Contraseña de aplicación** de 16 letras: Cuenta de Google →
   Seguridad → Verificación en dos pasos → Contraseñas de aplicaciones.
   No es tu contraseña normal de Gmail.
3. Copiá `.env.example` como `.env` y completá `GMAIL_USER` (tu correo)
   y `GMAIL_APP_PASS` (la contraseña de aplicación). El `.env` está en
   `.gitignore`: nunca se sube al repo.

#### Seguridad

| Medida | Qué hace |
|---|---|
| Simulación por defecto | Sin `--enviar` no manda nada, solo muestra |
| Confirmación | Pide `(s/n)` antes de enviar; cualquier otra respuesta cancela |
| Tope por corrida y diario | `--max` (20 por defecto), descontando lo ya enviado hoy |
| Pausa | 1 segundo entre emails, una sola conexión SMTP |
| Registro | Cada envío y cada error queda en `envios.log` |
| Descartes con aviso | Email inválido o columna faltante: avisa y sigue con el resto |

El registro de lo enviado (con los direcciones tapadas):

![Registro de envíos en envios.log](docs/envios_log.png)

> 💡 Problemas de red: el envío usa SSL directo por el puerto 465
> (probado en una red que bloqueaba el 587). Si tu red bloquea el 465,
> probá al revés: `smtplib.SMTP("smtp.gmail.com", 587)` + `starttls()`.
