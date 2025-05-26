import logging
import os

from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk

# 設定 Sentry（只會在第一次 import logger.py 時初始化）
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENV")

if SENTRY_DSN:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,       # 將 info+ 訊息作為 breadcrumb
        event_level=logging.ERROR # 只有 ERROR+ 會當作事件送出
    )
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENV,
        integrations=[sentry_logging],
        _experiments={
            "enable_logs": True
        }
    )

# 建立 logger
logger = logging.getLogger("tarot_backend")
logger.setLevel(logging.INFO)

# 加上 Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(console_handler)