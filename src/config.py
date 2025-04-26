# ../AgentConversationRetrievalSystem-worktrees/issue-3/src/config.py
import logging
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# プロジェクトルートディレクトリを基準にパスを設定
# このファイル (config.py) は src/ にある想定
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """
    アプリケーション設定を管理するクラス。
    環境変数または .env ファイルから読み込まれます。
    """

    # .env ファイルの場所とエンコーディングを指定
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8"
    )

    # データベース設定
    DB_PATH: Path = PROJECT_ROOT / "data" / "acrs.db"

    # ロギング設定
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FILE_PATH: Path | None = (
        PROJECT_ROOT / "logs" / "app.log"
    )  # Noneでファイル出力無効

    # LLMモデル設定
    CONVERSATION_MODEL: str = (
        "default-conversation-model"  # 会話生成モデル名 (適切なデフォルト値に変更)
    )
    SUMMARIZATION_MODEL: str = "hf.co/mmnga/ArrowMint-Gemma3-4B-YUKI-v0.1-gguf:latest"
    EMBEDDING_MODEL: str = "pfnet/plamo-embedding-1b"
    RERANKER_MODEL: str = "hotchpotch/japanese-reranker-cross-encoder-large-v1"

    # 他に必要な設定項目があればここに追加


# 設定クラスのインスタンスを作成
# モジュールインポート時に .env ファイル等が読み込まれる
settings = Settings()

# 例: ログレベルを数値に変換 (loggingライブラリで使用するため)
LOG_LEVEL_MAP = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}
numeric_log_level = LOG_LEVEL_MAP.get(settings.LOG_LEVEL.upper(), logging.INFO)

if __name__ == "__main__":
    # 設定内容を確認するための簡単なテストコード
    print("--- Application Settings ---")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"DB Path: {settings.DB_PATH}")
    print(f"Log Level: {settings.LOG_LEVEL} ({numeric_log_level})")
    print(f"Log File Path: {settings.LOG_FILE_PATH}")
    print(f"Conversation Model: {settings.CONVERSATION_MODEL}")
    print(f"Summarization Model: {settings.SUMMARIZATION_MODEL}")
    print(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    print(f"Reranker Model: {settings.RERANKER_MODEL}")
    print("--------------------------")
