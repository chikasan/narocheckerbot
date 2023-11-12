from abc import ABCMeta, abstractmethod
from typing import Any, Dict


class NovelConfigration(metaclass=ABCMeta):
    """各設定の基本クラス."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(self, url: Dict[Any, Any]):
        pass

    @abstractmethod
    def delete(self, ncode: str) -> Dict[Any, Any]:
        pass

    pass
