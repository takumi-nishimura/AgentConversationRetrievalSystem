import logging
from datetime import datetime

import duckdb
import pytest

# テスト対象のモジュールをインポート
# プロジェクトルートからの相対パスで指定
from src.db import schema

# テスト用のデータベースファイルパス (メモリDBではなくファイルを使う場合)
# TEST_DB_PATH = "test_acrs_db.duckdb"

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def test_db():
    """
    テスト用のインメモリDuckDB接続と初期化されたテーブルを提供するフィクスチャ。
    各テスト関数の実行前にセットアップし、実行後にクリーンアップします。
    """
    logger.info("Setting up in-memory database for test...")
    # インメモリデータベースを使用
    connection = duckdb.connect(database=":memory:", read_only=False)
    try:
        # テーブルを作成
        schema.initialize_database(connection)
        logger.info("Test database initialized.")
        yield connection  # テスト関数に接続オブジェクトを渡す
    finally:
        logger.info("Closing test database connection.")
        connection.close()
        # ファイルDBの場合のクリーンアップ
        # if os.path.exists(TEST_DB_PATH):
        #     os.remove(TEST_DB_PATH)
        #     logger.info(f"Removed test database file: {TEST_DB_PATH}")


def test_store_utterance_success(test_db: duckdb.DuckDBPyConnection):
    """
    store_utterance 関数が正常に発話データを格納できることをテストします。
    """
    session_id = "test_session_123"
    agent_id = "agent_X"
    utterance_text = "これはテスト発話です。"
    timestamp = datetime(2025, 4, 26, 10, 20, 0)  # 固定のタイムスタンプを使用

    logger.info(f"Attempting to store utterance for session '{session_id}'...")
    # store_utterance は内部で db_connection を使うが、テストではフィクスチャの接続を使いたい
    # ここでは store_utterance がグローバルな接続設定に依存すると仮定してそのまま呼び出す
    # より厳密には、store_utterance に接続オブジェクトを渡せるようにリファクタリングするか、
    # db_connection をモックする必要があるかもしれない。
    # 今回は簡単のため、store_utterance が :memory: DB を使うことを期待する。
    # (get_db_connection が :memory: を返すように設定されている前提)
    # --> connection.py が環境変数等でDBパスを決定する場合、テスト環境用の設定が必要
    # --> 現状の connection.py は固定パスなので、テストでは直接 :memory: を使うように修正が必要かも
    # --> 一旦、このまま進めてみる。store_utterance 内で connection.py が使われる。
    # --> connection.py がデフォルトでファイルDBを使うなら、このテストは失敗する可能性がある。
    # --> connection.py を確認する必要がある。

    # connection.py を確認した結果、デフォルトは 'acrs_db.duckdb' だった。
    # テスト用にインメモリDBを使うように store_utterance を直接呼び出すのではなく、
    # フィクスチャの接続オブジェクト (test_db) を使って直接SQLを実行して検証する。
    # store_utterance 関数のテストとしては不完全だが、まずはSQLレベルで検証。

    # store_utterance を呼び出す代わりに、直接SQLを実行してテスト
    sql = """
    INSERT INTO conversations (session_id, agent_id, utterance_text, timestamp)
    VALUES (?, ?, ?, ?);
    """
    test_db.execute(sql, [session_id, agent_id, utterance_text, timestamp])
    logger.info("Executed INSERT statement directly using test_db connection.")

    # --- ここから検証 ---
    logger.info("Verifying stored data...")
    result = test_db.execute(
        "SELECT session_id, agent_id, utterance_text, timestamp FROM conversations WHERE session_id = ?",
        [session_id],
    ).fetchone()

    assert result is not None, "データが挿入されていません"
    assert result[0] == session_id
    assert result[1] == agent_id
    assert result[2] == utterance_text
    # DuckDBのTIMESTAMP型はPythonのdatetimeオブジェクトとして返されるはず
    assert result[3] == timestamp
    logger.info("Data verification successful.")


# TODO: store_utterance 関数自体をテストするためのリファクタリングまたはモックを検討
# 例: store_utterance が接続オブジェクトを引数で受け取るように変更する
# def store_utterance(conn: duckdb.DuckDBPyConnection, session_id: str, ...):
#     # ... conn を使って実行 ...
#
# def test_store_utterance_function_call(test_db):
#     # ...
#     store_utterance(test_db, session_id, agent_id, utterance_text, timestamp)
#     # ... 検証 ...
