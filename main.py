import os
from dotenv import load_dotenv
load_dotenv()

from exchange_rete.boc.crawler import BocCrawler
from exchange_rete.boc.parser import BocParser
from exchange_rete.boc.config import BocStorage

def main():
    # 下载、解析（同上）
    crawler = BocCrawler(timeout=15)
    html = crawler.fetch()
    parser = BocParser()
    rates = parser.parse(html)

    # 存储
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("未找到 DATABASE_URL 环境变量")

    storage = BocStorage(db_url)
    storage.save_rates(rates)
    print("存储完成")

if __name__ == "__main__":
    main()