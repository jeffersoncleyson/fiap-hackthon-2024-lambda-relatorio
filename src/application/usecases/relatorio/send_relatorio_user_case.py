import json
import logging
from datetime import datetime, timezone

from src.application.usecases.relatorio.create_relatorio_user_case import (
    CreateReportUseCase,
)
from src.application.usecases.relatorio.read_last_month_ponto_user_case import (
    ReadLastMonthPontoUseCase,
)
from src.framework.adapters.output.email.email import EmailSenderAdapter
from src.framework.adapters.input.rest.response_formatter_utils import (
    ResponseFormatterUtils,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SendRelatorioUseCase:

    def __init__(
        self,
        email_sender: EmailSenderAdapter,
        read_by_month_use_case: ReadLastMonthPontoUseCase,
        create_report_use_case: CreateReportUseCase,
    ):
        self.email_sender = email_sender
        self.read_by_month_use_case = read_by_month_use_case
        self.create_report_use_case = create_report_use_case

    def process(self, event: dict):

        body_json = json.loads(event["body"])

        recipient_email = body_json.get("email")

        if not recipient_email:
            return ResponseFormatterUtils.get_response_message(
                {"error": "Email do destinatário é necessário."},
                400,
            )

        # Obtém os registros do último mês para o usuário
        logger.info("Read By Month")
        records = self.read_by_month_use_case.process(event)
        if not records:
            return ResponseFormatterUtils.get_response_message(
                {"error": "Nenhum registro encontrado para o mês anterior."},
                404,
            )

        # Gera o relatório com os registros
        logger.info("Create Report")
        report = self.create_report_use_case.process(event, records)

        logger.info("Report")
        logger.info(report)

        # Envia o relatório por e-mail
        try:
            self.email_sender.send(recipient_email, "Relatório de Ponto Mensal", report)
            return ResponseFormatterUtils.get_response_message(
                {"message": "Relatório enviado com sucesso."},
                200,
            )
        except Exception as e:
            return ResponseFormatterUtils.get_response_message(
                {"error": "Erro ao enviar o relatório"},
                500,
            )
