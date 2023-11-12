from typing import Dict

from narocheckerbot.naro18_api_gateway import Naro18ApiGateway
from narocheckerbot.naro_api_gateway import NaroApiGateway
from narocheckerbot.webapi_gateway import WebApiGateway


class ApiGatewayManager:
    def __init__(self) -> None:
        # サポートサイトの種類
        self._support = ["naro", "naro18"]
        self.support_sites: Dict[str, WebApiGateway] = {}
        for support_site in self._support:
            self.support_sites[support_site] = self.factory_config(support_site)

    def factory_config(self, site: str) -> WebApiGateway:
        """config生成用のfactory関数.

        Args:
            site (str): サポートサイト

        Raises:
            KeyError: 対象外のサイトを指定

        Returns:
            WebApiGateway: apigateway
        """
        if site == "naro":
            return NaroApiGateway()
        if site == "naro18":
            return Naro18ApiGateway()
        else:
            raise KeyError("サポート外")

    def get_gateway(self, site: str) -> WebApiGateway:
        """サイト別の設定を取得

        Args:
            site (str): サポートサイト名称

        Returns:
            NaroConfigration: _description_
        """
        return self.support_sites[site]

    pass
