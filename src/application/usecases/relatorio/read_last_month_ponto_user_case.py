from datetime import datetime, timedelta
import pytz
import logging

from src.framework.adapters.output.persistence.documentdb.documentdb import (
    DocumentDBAdapter,
)

from src.application.utils.ponto_utils import PontoUtils

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ReadLastMonthPontoUseCase:

    def __init__(self, mongo_client: DocumentDBAdapter):
        self.timezone = pytz.timezone('America/Sao_Paulo')
        self.mongo_client = mongo_client

    def process(self, event: dict):

        user_id = event["headers"]["x-sid"]

        logger.info(f"Read By Month user id {user_id}")

        now = datetime.now(tz=self.timezone)
        first_day_last_month = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = now.replace(day=1) - timedelta(days=1)
        start_date = first_day_last_month.strftime('%Y-%m-%d')
        end_date = last_day_last_month.strftime('%Y-%m-%d')

        query = {"user_id": user_id, "data": {"$gte": start_date, "$lte": end_date}}

        logger.info(f"Read By Month query {query}")

        results = self.mongo_client.read_all(query)

        logger.info(results)

        formatted_results = []
        for result in results:
            total_hours = PontoUtils.calculate_total_hours(result.get('array_ponto', []))
            formatted_result = {
                "data": result['data'],
                "hours": result.get('array_ponto', []),
                "total_hours": total_hours
            }
            formatted_results.append(formatted_result)

        return formatted_results
