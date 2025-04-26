import logging
from contextlib import contextmanager
from typing import Generator

import duckdb

from src.config import settings

logger = logging.getLogger(__name__)


def get_db_connection() -> duckdb.DuckDBPyConnection:
    """
    DuckDBデータベースへの接続を取得します。

    Returns:
        duckdb.DuckDBPyConnection: データベース接続オブジェクト。

    Raises:
        duckdb.Error: データベース接続に失敗した場合。
    """
    try:
        # データベースファイルが存在するディレクトリを作成 (なければ)
        settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(database=str(settings.DB_PATH), read_only=False)
        logger.info(f"Successfully connected to database: {settings.DB_PATH}")
        return conn
    except duckdb.Error as e:
        logger.error(f"Failed to connect to database: {settings.DB_PATH}. Error: {e}")
        raise


@contextmanager
def db_connection() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """
    データベース接続を管理するコンテキストマネージャ。
    接続の取得とクローズを自動で行います。

    Yields:
        duckdb.DuckDBPyConnection: データベース接続オブジェクト。

    Raises:
        duckdb.Error: データベース接続または切断に失敗した場合。
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    except duckdb.Error:
        # get_db_connection内で既にログ出力されているため、ここでは再raiseのみ
        raise
    finally:
        if conn:
            try:
                conn.close()
                logger.info(f"Database connection closed: {settings.DB_PATH}")
            except duckdb.Error as e:
                logger.error(
                    f"Failed to close database connection: {settings.DB_PATH}. Error: {e}"
                )
                # クローズ失敗は致命的ではない場合もあるため、ここではログ出力に留める
                # 必要であれば raise e を追加


if __name__ == "__main__":
    # 簡単な接続テスト
    logging.basicConfig(level=logging.INFO)
    try:
        with db_connection() as conn:
            logger.info("Connection test successful.")
            # 簡単なクエリを実行してみる
            result = conn.execute("SELECT 42;").fetchone()
            logger.info(f"Query result: {result}")
    except duckdb.Error as e:
        logger.error(f"Connection test failed: {e}")
