from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Optional


class WebApiGateway(metaclass=ABCMeta):
    """WebApiをもとに情報取得するための基底クラス.

    Args:
        metaclass (_type_, optional): _description_. Defaults to ABCMeta.
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    async def exec(self, urls: Optional[List[Dict[str, Any]]]) -> List[str]:
        pass

    @abstractmethod
    def create_query(self, id: Any) -> str:
        pass

    # @abstractmethod
    # async def request(self, url: Dict[str, Any]) -> Tuple[datetime, str]:
    #     pass
