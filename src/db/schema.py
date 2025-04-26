import logging

import duckdb

logger = logging.getLogger(__name__)

# テーブルスキーマ定義 (要件定義書 4.3 準拠)
# conversations テーブル: 会話の生データ
CREATE_CONVERSATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,                 -- 発話ごとのユニークID (自動採番を想定)
    session_id VARCHAR NOT NULL,            -- 会話セッションID
    agent_id VARCHAR NOT NULL,              -- 発話したエージェントのID
    utterance_text VARCHAR NOT NULL,        -- 発話内容
    timestamp TIMESTAMP NOT NULL,           -- 発話タイムスタンプ
    created_at TIMESTAMP DEFAULT current_timestamp -- レコード作成日時
);
"""

# conversation_summaries テーブル: 要約とベクトル
CREATE_CONVERSATION_SUMMARIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS conversation_summaries (
    id INTEGER PRIMARY KEY,                 -- 要約ごとのユニークID (自動採番を想定)
    conversation_session_id VARCHAR NOT NULL, -- 対応する会話セッションID (conversations.session_id と関連)
    summary_text VARCHAR NOT NULL,          -- 生成された要約テキスト
    embedding FLOAT[],                      -- 要約テキストの埋め込みベクトル (次元数はモデル依存)
    created_at TIMESTAMP DEFAULT current_timestamp -- レコード作成日時
);
"""
# TODO: embedding の次元数を設定ファイル等で管理できるようにする

# インデックス定義 (要件定義書 4.3 準拠)
# ベクトル検索インデックス (HNSW)
# 注意: DuckDBのvss拡張機能が必要。また、次元数(dims)は埋め込みモデルに合わせる必要がある。
# 例: CREATE INDEX IF NOT EXISTS summary_embedding_idx ON conversation_summaries USING HNSW (embedding) WITH (dims=1024, metric='cosine');
# 全文検索インデックス (fts拡張機能)
# 注意: DuckDBのfts拡張機能と、日本語トークナイザ(例: icu)の連携設定が必要。
# 例: PRAGMA create_fts_index('conversation_summaries', 'id', 'summary_text', overwrite=1, stemmer='icu', stopwords='none');


def initialize_database(connection: duckdb.DuckDBPyConnection):
    """
    データベースに必要なテーブルが存在しない場合に作成します。

    Args:
        connection: DuckDBデータベース接続オブジェクト。

    Raises:
        duckdb.Error: テーブル作成に失敗した場合。
    """
    try:
        logger.info("Initializing database tables if they don't exist...")
        connection.execute(CREATE_CONVERSATIONS_TABLE_SQL)
        logger.info("Checked/Created 'conversations' table.")
        connection.execute(CREATE_CONVERSATION_SUMMARIES_TABLE_SQL)
        logger.info("Checked/Created 'conversation_summaries' table.")
        logger.info("Database initialization complete.")
        # 注意: インデックス作成はここでは行わない。
        # ベクトル/全文検索インデックスは、データ挿入後や別途スクリプトで作成することを推奨。
        # また、必要な拡張機能(vss, fts, icu)のインストールとロードが前提となる。
    except duckdb.Error as e:
        logger.error(f"Failed to initialize database tables. Error: {e}")
        raise


if __name__ == "__main__":
    # 簡単な初期化テスト
    # スクリプトとして直接実行する場合、同じディレクトリ内の connection を直接インポート
    try:
        from connection import db_connection
    except ImportError:
        # もし PYTHONPATH が設定されていない場合など
        logger.error(
            "Could not import 'connection'. Make sure connection.py is in the same directory."
        )
        raise

    logging.basicConfig(level=logging.INFO)
    logger.info("Running schema initialization test...")
    try:
        with db_connection() as conn:
            initialize_database(conn)
            logger.info("Schema initialization test successful.")
            # テーブル構造を確認 (オプション)
            # print("\nTables:")
            # print(conn.execute("SHOW TABLES;").fetchall())
            # print("\nConversations Schema:")
            # print(conn.execute("DESCRIBE conversations;").fetchall())
            # print("\nConversation Summaries Schema:")
            # print(conn.execute("DESCRIBE conversation_summaries;").fetchall())
    except duckdb.Error as e:
        logger.error(f"Schema initialization test failed: {e}")
    except ImportError:
        logger.error(
            "Could not import db_connection. Make sure connection.py is in the same directory or PYTHONPATH is set correctly."
        )
