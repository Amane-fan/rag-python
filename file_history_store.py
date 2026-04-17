import json
import os
import re
from typing import List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


def build_history_file_path(base_dir: str, session_id: str) -> str:
    """根据会话ID生成安全的历史文件路径"""
    normalized_session_id = session_id.strip() or "default"
    safe_session_id = re.sub(r"[^a-zA-Z0-9._-]", "_", normalized_session_id)
    return os.path.join(base_dir, f"{safe_session_id}.json")


def list_history_session_ids(base_dir: str) -> List[str]:
    """列出已有的历史会话ID"""
    if not os.path.exists(base_dir):
        return []
    session_ids = []
    for file_name in os.listdir(base_dir):
        if file_name.endswith(".json"):
            session_ids.append(file_name[:-5])
    return sorted(session_ids)


class FileHistoryStore(BaseChatMessageHistory):
    """将会话历史持久化到本地JSON文件"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._write_messages([])

    @property
    def messages(self) -> List[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                raw_messages = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        return messages_from_dict(raw_messages)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        stored_messages = self.messages
        stored_messages.extend(messages)
        self._write_messages(stored_messages)

    def clear(self) -> None:
        self._write_messages([])

    def _write_messages(self, messages: List[BaseMessage]) -> None:
        payload = [message_to_dict(message) for message in messages]
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
