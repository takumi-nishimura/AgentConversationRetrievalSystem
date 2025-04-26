import logging
import sys
from logging.handlers import RotatingFileHandler

from src.config import PROJECT_ROOT, numeric_log_level, settings


def setup_logging():
    """
    アプリケーションのロギングを設定します。

    設定ファイル (src/config.py) から読み込んだ値に基づき、
    標準出力とファイルへのログ出力を設定します。
    """
    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s] [%(name)s] [%(threadName)s] %(message)s (%(filename)s:%(lineno)d)"
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_log_level)

    # 標準出力ハンドラ
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    root_logger.addHandler(stream_handler)

    # ファイル出力ハンドラ (LOG_FILE_PATHが設定されている場合)
    if settings.LOG_FILE_PATH:
        # ログディレクトリが存在しない場合は作成
        log_dir = settings.LOG_FILE_PATH.parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # ローテーション設定 (例: 1ファイル10MB, 5世代まで保持)
        file_handler = RotatingFileHandler(
            settings.LOG_FILE_PATH,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

    # 主要ライブラリのログレベル調整 (必要に応じて)
    # logging.getLogger("uvicorn").setLevel(logging.WARNING)
    # logging.getLogger("httpx").setLevel(logging.INFO)

    logging.info("Logging setup complete.")
    logging.info(f"Log level set to: {settings.LOG_LEVEL}")
    if settings.LOG_FILE_PATH:
        logging.info(f"Logging to file: {settings.LOG_FILE_PATH}")
    else:
        logging.info("File logging is disabled.")


if __name__ == "__main__":
    # モジュール単体で実行した場合のテスト用コード
    setup_logging()
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")

    try:
        1 / 0
    except ZeroDivisionError:
        logging.exception("An exception occurred!")

    logging.info(f"Project Root: {PROJECT_ROOT}")
    logging.info(f"Settings DB Path: {settings.DB_PATH}")
