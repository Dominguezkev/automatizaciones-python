# enviar_emails.py: simula por defecto, solo envía con --enviar
import argparse
import csv
import logging
import re
import smtplib
import time

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()  # carga GMAIL_USER y GMAIL_APP_PASS desde .env (para el envío real)
EMAIL_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")  # chequeo básico

logging.basicConfig(filename="envios.log", level=logging.INFO,
                    format="%(asctime)s %(message)s")


def preparar(contactos, plantilla):
    """Devuelve (listos, descartados). No envía nada."""
    listos, descartados = [], []
    for fila in contactos:
        email = (fila.get("email") or "").strip()
        if not EMAIL_VALIDO.match(email):
            descartados.append((fila.get("nombre"), f"email inválido: '{email}'"))
            continue
        try:
            texto = plantilla.format_map(fila)  # reemplaza {nombre}, {turno}...
        except KeyError as e:
            descartados.append((fila.get("nombre"), f"falta la columna {e}"))
            continue
        listos.append((email, texto))
    return listos, descartados


def main():
    p = argparse.ArgumentParser(description="Envía emails personalizados")
    p.add_argument("contactos", help="CSV con columnas nombre,email,...")
    p.add_argument("--plantilla", default="plantilla.txt")
    p.add_argument("--asunto", default="Recordatorio")
    p.add_argument("--max", type=int, default=20, help="Tope de envíos por corrida")
    p.add_argument("--enviar", action="store_true", help="Envía de verdad (sin esto, solo simula)")
    args = p.parse_args()

    if args.max < 1:
        print("❌ --max tiene que ser 1 o más.")
        return

    try:
        with open(args.contactos, newline="", encoding="utf-8-sig") as f:
            contactos = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"❌ No encontré el archivo de contactos '{args.contactos}'.")
        return
    except UnicodeDecodeError:
        print(f"❌ '{args.contactos}' no se pudo leer como texto. ¿Es un CSV de verdad?")
        return

    try:
        with open(args.plantilla, encoding="utf-8") as f:
            plantilla = f.read()
    except FileNotFoundError:
        print(f"❌ No encontré la plantilla '{args.plantilla}'.")
        return

    listos, descartados = preparar(contactos, plantilla)

    for nombre, motivo in descartados:
        print(f"⚠️  Descartado ({nombre}): {motivo}")

    if len(listos) > args.max:
        print(f"⚠️  Hay {len(listos)} emails y el tope es {args.max}: "
              f"se envían solo los primeros {args.max}.")
        listos = listos[:args.max]

    for email, texto in listos:
        print(f"✉️  {email}: {texto}")

    if not args.enviar:
        print(f"\n🔎 Simulación: se enviarían {len(listos)} emails, "
              f"{len(descartados)} descartados. No se envió nada.")
        return

    print("\n(El envío real lo agregamos mañana.)")


if __name__ == "__main__":
    main()
