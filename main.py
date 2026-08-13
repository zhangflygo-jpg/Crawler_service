import os
import traceback
from datetime import datetime

from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from exchange_rete.boc.crawler import BocCrawler
from exchange_rete.boc.parser import BocParser
from exchange_rete.boc.config import BocStorage


load_dotenv()


def job():
    """执行一次汇率爬取和存储任务"""

    start_time = datetime.now()

    print("=" * 50)
    print(f"开始执行汇率任务 | 执行时间: {start_time:%Y-%m-%d %H:%M:%S}")
    print("=" * 50)

    try:
        # 1. 爬取
        crawler = BocCrawler(timeout=15)
        html = crawler.fetch()

        # 2. 解析
        parser = BocParser()
        rates = parser.parse(html)

        print(f"解析到 {len(rates)} 条汇率数据")

        # 3. 获取数据库配置
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            raise RuntimeError("未找到 DATABASE_URL 环境变量")

        # 4. 保存到数据库
        storage = BocStorage(db_url)
        storage.save_rates(rates)

        end_time = datetime.now()
        duration = end_time - start_time

        print("汇率数据存储成功")
        print(f"任务完成时间: {end_time:%Y-%m-%d %H:%M:%S}")
        print(f"任务耗时: {duration}")
        print("=" * 50)
        print()

    except Exception as e:
        error_time = datetime.now()

        print(f"任务执行失败 | 时间: {error_time:%Y-%m-%d %H:%M:%S}")
        print(f"错误: {e}")
        traceback.print_exc()


def main():

    scheduler = BlockingScheduler()

    # 启动时立即执行一次
    job()

    # 每天 09:31 执行
    scheduler.add_job(
        job,
        trigger=CronTrigger(
            hour=9,
            minute=31,
            timezone="Asia/Shanghai"
        ),
        id="boc_exchange_rate_daily",
        replace_existing=True,
    )

    print("=" * 50)
    print("汇率爬虫定时任务已启动")
    print("每天执行时间: 09:31")
    print(f"当前启动时间: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("时区: Asia/Shanghai")
    print("=" * 50)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("定时任务已停止")


if __name__ == "__main__":
    main()