# enviar_emails.py: simula por defecto, solo envía con --enviar
import argparse
import csv
import logging
import os
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


def enviar_real(listos, asunto):
    """Envía de verdad. Una sola conexión SMTP y un try/except por contacto.

    Devuelve la cantidad de emails enviados (0 si se cancela o falla todo).
    """
    usuario = os.environ.get("GMAIL_USER", "").strip()
    clave = os.environ.get("GMAIL_APP_PASS", "").strip()
    if not usuario or not clave:
        print("❌ Faltan GMAIL_USER/GMAIL_APP_PASS. Copiá .env.example como .env "
              "y completá tus datos (ver comentarios del propio archivo).")
        return 0

    print(f"\nVas a enviar {len(listos)} emails. ¿Seguro? (s/n)")
    try:
        respuesta = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        respuesta = ""          # sin respuesta clara -> no se envía nada
    if respuesta not in ("s", "si", "sí", "y", "yes"):
        print("Cancelado: no se envió nada.")
        return 0

    # Una sola conexión para todos los emails (abrir una por contacto es lento
    # y llama más la atención de los servidores de correo).
    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(usuario, clave)
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail rechazó las credenciales. Revisá GMAIL_USER y que "
              "GMAIL_APP_PASS sea una Contraseña de aplicación (16 letras, "
              "sin la contraseña normal de la cuenta).")
        logging.error("ERROR autenticación SMTP")
        return 0
    except OSError as e:
        print(f"❌ No se pudo conectar a Gmail: {e}")
        logging.error(f"ERROR conexión SMTP: {e}")
        return 0

    try:
        enviados = 0
        for i, (email, texto) in enumerate(listos):
            mensaje = EmailMessage()
            mensaje["From"] = usuario
            mensaje["To"] = email
            mensaje["Subject"] = asunto
            mensaje.set_content(texto)
            try:
                servidor.send_message(mensaje)
                enviados += 1
                logging.info(f"OK {email}")
                print(f"✔ Enviado a {email}")
            except (smtplib.SMTPException, OSError) as e:
                # Si un contacto falla, se anota y se sigue con el resto
                motivo = str(e) or type(e).__name__
                logging.error(f"ERROR {email}: {motivo}")
                print(f"❌ Falló {email}: {motivo} (sigue con los demás)")
            # Pausa entre emails (no después del último) para no parecer spam
            if i < len(listos) - 1:
                time.sleep(1)
    finally:
        servidor.quit()

    print(f"\n✉️  Listo: {enviados} enviados, {len(listos) - enviados} fallados. "
          f"El detalle quedó en envios.log")
    return enviados


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

    enviar_real(listos, args.asunto)


if __name__ == "__main__":
    main()
