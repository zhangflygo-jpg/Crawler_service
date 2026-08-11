from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BocParser:
    """中国银行汇率数据解析器"""

    TARGET_CURRENCY = {"美元", "港币", "欧元"}
    
    def parse(self, html: str) -> List[Dict]:
        """
        解析汇率HTML
        
        Args:
            html: 网页HTML字符串
            
        Returns:
            List[Dict]: 解析后的汇率数据列表
            
        Raises:
            ValueError: 解析失败时抛出
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            table = self._find_rate_table(soup)
            
            if not table:
                raise ValueError("未找到汇率表格")
            
            rows = table.find_all("tr")
            if len(rows) < 2:
                raise ValueError("表格格式异常")
            
            result = []
            for row in rows[1:]:
                record = self._parse_row(row)
                if record:
                    result.append(record)
            
            if not result:
                raise ValueError("未提取到目标货币汇率")
            
            logger.info(f"成功解析 {len(result)} 条汇率数据")
            return result
            
        except Exception as e:
            logger.error(f"解析失败: {e}")
            raise
    
    def _find_rate_table(self, soup: BeautifulSoup) -> Optional[any]:
        """智能查找汇率表格"""
        tables = soup.find_all("table")
        
        for table in tables:
            first_row = table.find("tr")
            if first_row and "货币名称" in first_row.get_text():
                return table
        
        # 降级方案
        return tables[1] if len(tables) > 1 else None
    
    def _parse_row(self, row) -> Optional[Dict]:
        """解析单行数据"""
        cols = row.find_all("td")
        if len(cols) < 8:
            return None
        
        currency = cols[0].get_text(strip=True)
        
        if currency not in self.TARGET_CURRENCY:
            return None
        
        try:
            return {
                "currency": currency,
                "buying_rate": self._to_float(cols[1].get_text(strip=True)),
                "cash_buying_rate": self._to_float(cols[2].get_text(strip=True)),
                "selling_rate": self._to_float(cols[3].get_text(strip=True)),
                "cash_selling_rate": self._to_float(cols[4].get_text(strip=True)),
                "middle_rate": self._to_float(cols[5].get_text(strip=True)),
                "publish_date": cols[6].get_text(strip=True),
                "publish_time": cols[7].get_text(strip=True),
            }
        except Exception as e:
            logger.warning(f"解析 {currency} 数据失败: {e}")
            return None
    
    @staticmethod
    def _to_float(value: str) -> float:
        """安全的字符串转浮点数"""
        if not value or value.strip() in ["", "-", "--"]:
            return 0.0
        return float(value.replace(",", "").replace("%", ""))