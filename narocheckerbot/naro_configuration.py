from typing import Any, Dict, List

from narocheckerbot.novel_configration import NovelConfigration


class NaroConfigration(NovelConfigration):
    """なろうAPIのデータ管理クラス.

    Args:
        NovelConfigration (_type_): _description_
    """

    def __init__(self, urls: List[Dict[Any, Any]]) -> None:
        # TODO: データが正しいかどうかの確認
        self.urls = urls
        super().__init__()

    def add(self, url: Dict[Any, Any]):
        """_summary_

        Args:
            url (Dict[Any, Any]): _description_
        """
        self.urls.append(url)

    def delete(self, ncode: str) -> Dict[Any, Any]:
        """指定したncodeに対応する小説を削除する。

        Args:
            ncode (str): _description_

        Returns:
            Dict[Any, Any]: _description_
        """
        removed_value: Dict[Any, Any] = {}

        for index, url in enumerate(self.urls):
            if url["ncode"] == ncode:
                removed_value = self.urls.pop(index)

        return removed_value

    def is_exist_account(self, ncode: str) -> bool:
        """リスト登録済みかの確認.

        Args:
            ncode (str): _description_

        Returns:
            bool: 登録済みならTrue, そうでなければFalse
        """
        for url in self.urls:
            if url["ncode"] == ncode:
                return True

        return False

    pass
