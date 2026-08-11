# app/crawlers/exchange_rate/boc/crawler.py

import requests

class BocCrawler:
    """中国银行汇率网页下载器"""

    URL = "https://www.boc.cn/sourcedb/whpj/"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch(self) -> str:
        """
        下载网页HTML

        Returns:
            str: 网页HTML
        """

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0 Safari/537.36"
            )
        }

        response = requests.get(
            self.URL,
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        # 自动识别网页编码
        response.encoding = response.apparent_encoding

        return response.text