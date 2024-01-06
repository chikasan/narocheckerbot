import os
from logging import getLogger
from typing import Any, Dict, Union

from ruamel.yaml import YAML

from narocheckerbot.naro_blog_configuration import NaroBlogConfigration
from narocheckerbot.naro_configuration import NaroConfigration


class ConfigManager:
    """_summary_."""

    def __init__(self) -> None:
        """初期化."""
        self._logger = getLogger("narocheckerlog.config")
        self._configfile = os.path.dirname(os.path.abspath(__file__)) + "/config.yaml"

        with open(self._configfile, "r") as stream:
            yaml = YAML()
            self._yaml_data = yaml.load(stream)

        # サポートサイトの種類
        self._support = ["naro", "naro18", "naro_blog"]
        self.support_sites: Dict[str, Any] = {}
        for support_site in self._support:
            try:
                self.support_sites[support_site] = self.factory_config(support_site)
            except KeyError:
                "設定が見つからない場合、何もしない"
                pass

    def factory_config(
        self, site: str
    ) -> Union[NaroConfigration, NaroBlogConfigration]:
        """config生成用のfactory関数.

        Args:
            site (str): サポートサイト

        Raises:
            KeyError: 対象外のサイトを指定

        Returns:
            NaroConfigration: 生成したconfig
        """
        if site == "naro":
            return NaroConfigration(self._yaml_data[site])
        if site == "naro18":
            return NaroConfigration(self._yaml_data[site])
        if site == "naro_blog":
            return NaroBlogConfigration(self._yaml_data[site])
        else:
            raise KeyError("サポート外")

    def write_yaml(self):
        """設定ファイルへの書き込み."""
        with open(self._configfile, "w") as stream:
            yaml = YAML()
            yaml.dump(data=self._yaml_data, stream=stream)

    def get_config(self, site: str) -> Union[NaroConfigration, NaroBlogConfigration]:
        """サイト別の設定を取得

        Args:
            site (str): サポートサイト名称

        Returns:
            NaroConfigration: config
        """
        return self.support_sites[site]
