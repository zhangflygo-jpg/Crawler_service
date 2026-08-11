# exchange_rete/boc/config.py
import logging
from typing import List, Dict
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class BocStorage:
    """中国银行汇率存储（存入 crawler_service.exchange_rates）"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)

    def save_rates(self, rates: List[Dict]) -> int:
        """批量保存汇率，重复跳过，返回插入条数"""
        if not rates:
            return 0

        insert_sql = text("""
            INSERT IGNORE INTO exchange_rates
                (currency, buying_rate, cash_buying_rate, selling_rate,
                 cash_selling_rate, middle_rate, publish_date, publish_time)
            VALUES
                (:currency, :buying_rate, :cash_buying_rate, :selling_rate,
                 :cash_selling_rate, :middle_rate, :publish_date, :publish_time)
        """)

        records = self._prepare_data(rates)

        with self.engine.begin() as conn:
            result = conn.execute(insert_sql, records)
            inserted = result.rowcount
            logger.info(f"成功插入 {inserted} 条汇率记录")
            return inserted

    @staticmethod
    def _prepare_data(rates: List[Dict]) -> List[Dict]:
        """数据清洗：拆分日期/时间，数值除以100，空值转为0"""
        records = []
        for r in rates:
            raw_datetime = r.get("publish_date", "")
            time_str = r.get("publish_time", "")

            # 拆分日期和时间
            if " " in raw_datetime:
                parts = raw_datetime.split(" ")
                date_str = parts[0].replace("/", "-")
                if not time_str and len(parts) > 1:
                    time_str = parts[1]
            else:
                date_str = raw_datetime.replace("/", "-")

            records.append({
                "currency": r["currency"],
                "buying_rate": float(r["buying_rate"]) / 100 if r["buying_rate"] else 0.0,
                "cash_buying_rate": float(r["cash_buying_rate"]) / 100 if r["cash_buying_rate"] else 0.0,
                "selling_rate": float(r["selling_rate"]) / 100 if r["selling_rate"] else 0.0,
                "cash_selling_rate": float(r["cash_selling_rate"]) / 100 if r["cash_selling_rate"] else 0.0,
                "middle_rate": float(r["middle_rate"]) / 100 if r["middle_rate"] else 0.0,
                "publish_date": date_str,
                "publish_time": time_str,
            })
        return records