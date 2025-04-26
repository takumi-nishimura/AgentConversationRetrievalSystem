import logging
from datetime import datetime

import duckdb

# connection モジュールをインポート (同じ階層の db ディレクトリから)
# Python のモジュール解決のため、適切なパス設定や __init__.py が必要になる場合がある
try:
    from ..db.connection import db_connection
except ImportError:
    # 直接スクリプトとして実行する場合や、パスが通っていない場合のフォールバック
    # (通常はプロジェクトルートから実行されることを想定)
    from src.db.connection import db_connection


logger = logging.getLogger(__name__)


def store_utterance(
    session_id: str, agent_id: str, utterance_text: str, timestamp: datetime
):
    """
    単一の発話データを conversations テーブルに格納します。

    Args:
        session_id: 会話セッションID。
        agent_id: 発話したエージェントのID。
        utterance_text: 発話内容。
        timestamp: 発話タイムスタンプ。

    Raises:
        duckdb.Error: データベースへの挿入に失敗した場合。
        Exception: その他の予期せぬエラーが発生した場合。
    """
    sql = """
    INSERT INTO conversations (session_id, agent_id, utterance_text, timestamp)
    VALUES (?, ?, ?, ?);
    """
    try:
        with db_connection() as conn:
            conn.execute(sql, [session_id, agent_id, utterance_text, timestamp])
            logger.info(
                f"Stored utterance for session '{session_id}', agent '{agent_id}'."
            )
    except duckdb.Error as e:
        logger.error(
            f"Failed to store utterance for session '{session_id}'. DB Error: {e}"
        )
        raise
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while storing utterance for session '{session_id}': {e}"
        )
        raise


if __name__ == "__main__":
    # 簡単なテスト実行
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Running conversation_manager test...")

    # テスト用DBの初期化 (schema.py を利用)
    try:
        from ..db import schema
    except ImportError:
        from src.db import schema

    try:
        with db_connection() as conn:
            schema.initialize_database(conn)  # テーブルがなければ作成

        # テストデータの挿入
        test_session_id = "test_session_001"
        test_agent_id_1 = "agent_A"
        test_agent_id_2 = "agent_B"
        test_utterance_1 = "こんにちは、元気ですか？"
        test_utterance_2 = "はい、元気です。あなたは？"
        test_timestamp_1 = datetime.now()
        test_timestamp_2 = (
            datetime.now()
        )  # 少し時間をずらす方がリアルだが、テストなので同時刻でも可

        store_utterance(
            test_session_id, test_agent_id_1, test_utterance_1, test_timestamp_1
        )
        store_utterance(
            test_session_id, test_agent_id_2, test_utterance_2, test_timestamp_2
        )

        logger.info("Test utterances stored successfully.")

        # 格納されたデータの確認 (オプション)
        with db_connection() as conn:
            result = conn.execute(
                f"SELECT * FROM conversations WHERE session_id = '{test_session_id}' ORDER BY timestamp;"
            ).fetchall()
            logger.info(f"Stored data for session '{test_session_id}':")
            for row in result:
                logger.info(row)

    except duckdb.Error as e:
        logger.error(f"Conversation manager test failed during DB operation: {e}")
    except ImportError as e:
        logger.error(f"Conversation manager test failed due to import error: {e}")
    except Exception as e:
        logger.error(f"Conversation manager test failed with an unexpected error: {e}")
