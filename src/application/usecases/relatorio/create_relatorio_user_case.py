import logging
import pytz
from datetime import datetime, timedelta


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CreateReportUseCase:

    def __init__(self):
        self.timezone = pytz.timezone('America/Sao_Paulo')

    def process(self, event: dict, records: dict):

        user_id = event["headers"]["x-sid"]

        # Obtém o mês e o ano do último mês
        now = datetime.now(tz=self.timezone)
        first_day_last_month = now.replace(day=1) - timedelta(days=1)
        month_year = first_day_last_month.strftime("%m/%Y")

        # Inicia o HTML do relatório
        html = f"""
        <html>
            <head>
                <style>
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        border: 1px solid #dddddd;
                        text-align: left;
                        padding: 8px;
                    }}
                    th {{
                        background-color: #f2f2f2;
                    }}
                </style>
            </head>
            <body>
                <h2>{month_year} - Relatório de Ponto - {user_id}</h2>
                <table>
                    <tr>
                        <th>Listagem das datas</th>
                        <th>Batimentos de ponto</th>
                        <th>Total de horas trabalhadas</th>
                    </tr>
        """

        # Adiciona os registros ao HTML
        for record in records:
            hours_str = " ".join(record["hours"])
            html += f"""
                    <tr>
                        <td>{record['data']}</td>
                        <td>{hours_str}</td>
                        <td>{record['total_hours']}</td>
                    </tr>
            """

        # Fecha as tags do HTML
        html += """
                </table>
            </body>
        </html>
        """
        return html
