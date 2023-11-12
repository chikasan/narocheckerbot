import os
from logging import getLogger
from typing import Any, Dict, List

from ruamel.yaml import YAML


class ConfigManager:
    """_summary_."""

    def __init__(self) -> None:
        """初期化."""
        self._logger = getLogger("narocheckerlog.config")
        self._configfile = os.path.dirname(os.path.abspath(__file__)) + "/config.yaml"

        with open(self._configfile, "r") as stream:
            yaml = YAML()
            self._yaml_data = yaml.load(stream)

        # self.channel_id = self.yaml_data["channel"]
        pass

    def write_yaml(self):
        """設定ファイルへの書き込み."""
        with open(self._configfile, "w") as stream:
            yaml = YAML()
            yaml.dump(data=self._yaml_data, stream=stream)

    def get_urls(self) -> List[Dict[Any, Any]]:
        """URLリストを返す.

        Returns:
            Dict[Any, Any]: _description_
        """
        return self._yaml_data["naro"]["account"]

    def get_channel_id(self) -> int:
        """結果を書き込むチャンネルIDを返す.

        Returns:
            int: チャンネルID
        """
        return self._yaml_data["naro"]["channel"]

    pass
