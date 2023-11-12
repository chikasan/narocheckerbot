import os
from logging import getLogger
from typing import Any, Dict

from ruamel.yaml import YAML

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

        self._support = ["naro"]
        self.support_sites: Dict[str, Any] = {}
        for support_site in self._support:
            self.support_sites[support_site] = self.factory_config(support_site)

        # self.channel_id = self.yaml_data["channel"]
        pass

    def factory_config(self, site: str) -> NaroConfigration:
        if site == "naro":
            return NaroConfigration(self._yaml_data[site])
        else:
            raise KeyError("サポート外")

    def write_yaml(self):
        """設定ファイルへの書き込み."""
        with open(self._configfile, "w") as stream:
            yaml = YAML()
            yaml.dump(data=self._yaml_data, stream=stream)

    def get_config(self, site: str) -> NaroConfigration:
        """サイト別の設定を取得

        Args:
            site (str): サポートサイト名称

        Returns:
            NaroConfigration: _description_
        """
        return self.support_sites[site]
