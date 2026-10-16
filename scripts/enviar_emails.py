# enviar_emails.py
import smtplib, os
from email.message import EmailMessage
import pandas as pd

USUARIO = os.getenv("GMAIL_USER")   # NUNCA escribas claves directo en el código
CLAVE = os.getenv("GMAIL_APP_PASS")

def enviar(destino, asunto, cuerpo):
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = USUARIO, destino, asunto
    msg.set_content(cuerpo)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(USUARIO, CLAVE)
        servidor.send_message(msg)

contactos = pd.read_csv("contactos.csv")  # columnas: nombre, email, turno
for _, fila in contactos.iterrows():
    texto = f"Hola {fila['nombre']}, tu turno es el {fila['turno']}."
    enviar(fila["email"], "Recordatorio de turno", texto)
    print(f"✉️  Enviado a {fila['email']}")
