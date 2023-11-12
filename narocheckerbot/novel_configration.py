from abc import ABCMeta, abstractmethod
from typing import Any, Dict


class NovelConfigration(metaclass=ABCMeta):
    """各設定の基本クラス."""

    def __init__(self, urls: Any) -> None:
        """初期化.

        Args:
            urls (Any): _description_
        """
        self.urls = urls["account"]
        self.channel_id = urls["channel"]
        pass

    @abstractmethod
    def add(self, url: Dict[Any, Any]):
        pass

    @abstractmethod
    def delete(self, ncode: str) -> bool:
        pass

    pass
