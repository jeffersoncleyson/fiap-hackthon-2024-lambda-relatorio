import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.application.ports.output.email.smtp import SMTP

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EmailSenderAdapter:

    def __init__(self, smtp: SMTP):
        self.smtp = smtp

    def send(self, recipient_email: str, subject: str, data: str):
        # Configurações do servidor e credenciais do Yahoo
        smtp_server = self.smtp.server
        smtp_port = self.smtp.port
        smtp_user = self.smtp.user
        smtp_password = self.smtp.password

        # Criar a mensagem de e-mail
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(data, "html"))  # Alterado para 'html'

        # Enviar o e-mail usando o servidor SMTP do Yahoo
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        except Exception as err:
            logger.info("Error on sending message")
            logger.error(err)
