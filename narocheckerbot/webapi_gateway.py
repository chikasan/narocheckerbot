from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Any, Dict, Tuple


class WebApiGateway(metaclass=ABCMeta):
    """WebApiをもとに情報取得するための基底クラス.

    Args:
        metaclass (_type_, optional): _description_. Defaults to ABCMeta.
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def create_query(self, id: Any) -> str:
        pass

    @abstractmethod
    async def request(self, url: Dict[str, Any]) -> Tuple[datetime, str]:
        pass