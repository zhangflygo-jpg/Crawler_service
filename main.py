import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

from exchange_rete.boc.crawler import BocCrawler
from exchange_rete.boc.parser import BocParser
from exchange_rete.boc.config import BocStorage


load_dotenv()


def job():
    """执行一次汇率爬取和存储任务"""

    print("========== 开始执行汇率任务 ==========")

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

        print("汇率数据存储成功")
        print("========== 任务执行完成 ==========\n")

    except Exception as e:
        print(f"汇率任务执行失败: {e}")


def main():

    # 创建定时任务调度器
    scheduler = BlockingScheduler()

    # 启动程序时先立即执行一次
    job()

    # 每天 09:00 执行
    scheduler.add_job(
        job,
        trigger="cron",
        hour=9,
        minute=31,
        id="boc_exchange_rate_daily",
        replace_existing=True,
    )

    print("===================================")
    print("汇率爬虫定时任务已启动")
    print("每天 09:00 自动执行")
    print("===================================")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("定时任务已停止")


if __name__ == "__main__":
    main()