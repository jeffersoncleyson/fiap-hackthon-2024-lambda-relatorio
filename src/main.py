import logging

import pymongo
from src.application.ports.output.email.smtp import SMTP
from src.application.usecases.relatorio.create_relatorio_user_case import \
    CreateReportUseCase
from src.application.usecases.relatorio.read_last_month_ponto_user_case import \
    ReadLastMonthPontoUseCase
from src.application.usecases.relatorio.send_relatorio_user_case import \
    SendRelatorioUseCase
from src.application.utils.environment import EnvironmentUtils
from src.application.utils.environment_constants import EnvironmentConstants
from src.framework.adapters.input.rest.response_formatter_utils import \
    ResponseFormatterUtils
from src.framework.adapters.output.email.email import EmailSenderAdapter
from src.framework.adapters.output.persistence.documentdb.documentdb import \
    DocumentDBAdapter

logger = logging.getLogger()
logger.setLevel(logging.INFO)


mongo_uri = EnvironmentUtils.get_env(EnvironmentConstants.MONGO_URI.name)
database = EnvironmentUtils.get_env(EnvironmentConstants.DB_NAME.name)
database_client = pymongo.MongoClient(mongo_uri)
database_adapter = DocumentDBAdapter("pontos", database_client[database])
read_by_month_use_case = ReadLastMonthPontoUseCase(database_adapter)

create_report_use_case = CreateReportUseCase()

smtp_server = EnvironmentUtils.get_env(EnvironmentConstants.SMTP_SERVER.name)
smtp_port = EnvironmentUtils.get_env(EnvironmentConstants.SMTP_PORT.name)
smtp_user = EnvironmentUtils.get_env(EnvironmentConstants.SMTP_USER.name)
smtp_password = EnvironmentUtils.get_env(EnvironmentConstants.SMTP_PASSWORD.name)
smtp = SMTP(smtp_server, smtp_port, smtp_user, smtp_password)
email_sender = EmailSenderAdapter(smtp)
send_relatorio_use_case = SendRelatorioUseCase(email_sender, read_by_month_use_case, create_report_use_case)


def lambda_handler(event, context):

    resource_path = event["requestContext"]["resourcePath"]
    http_method = event["requestContext"]["httpMethod"]

    if http_method == "POST" and resource_path == "/report":
        return send_relatorio_use_case.process(event)

    return ResponseFormatterUtils.get_response_message(
        {
            "error": "not_found",
            "error_description": "%s %s is not a valid resource."
            % (http_method, resource_path),
        },
        404,
    )
