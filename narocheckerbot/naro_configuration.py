from typing import Any, Dict

from narocheckerbot.novel_configration import NovelConfigration


class NaroConfigration(NovelConfigration):
    """なろうAPIのデータ管理クラス.

    Args:
        NovelConfigration (_type_): 基底クラス
    """

    def __init__(self, urls: Any) -> None:
        # TODO: データが正しいかどうかの確認
        super().__init__(urls)

    def add(self, url: Dict[str, Any]):
        """_summary_

        Args:
            url (Dict[str, Any]): 追加したいデータ
        """
        self.urls.append(url)

    def delete(self, ncode: str) -> bool:
        """指定したncodeに対応する小説を削除する。

        Args:
            ncode (str): ncode

        Returns:
            bool: 削除を実行した場合はTrue, 見つからなければFalse
        """
        for index, url in enumerate(self.urls):
            if url["ncode"] == ncode:
                self.urls.pop(index)
                return True

        return False

    def is_exist_account(self, ncode: str) -> bool:
        """リスト登録済みかの確認.

        Args:
            ncode (str): ncode

        Returns:
            bool: 登録済みならTrue, そうでなければFalse
        """
        for url in self.urls:
            if url["ncode"] == ncode:
                return True

        return False

    pass
