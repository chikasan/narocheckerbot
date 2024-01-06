import asyncio
import itertools
from datetime import datetime
from logging import getLogger
from time import mktime
from typing import Any, Dict, List, Optional

import feedparser

from narocheckerbot.webapi_gateway import WebApiGateway


class NaroBlogApiGateway(WebApiGateway):
    """小説の更新確認を行う."""

    def __init__(self) -> None:
        """初期化."""
        self.logger = getLogger("narocheckerlog.naro_blog_api")
        self.sem = asyncio.Semaphore(10)

        # 抽象化のための情報
        self.id = "userid"

        pass

    async def exec(self, urls: Optional[List[Dict[str, Any]]]) -> List[str]:
        """チェック処理本体.

        Args:
            urls (Optional[List[Dict[str, Any]]]): ncodeと最終更新日を記載した辞書データ リスト

        Returns:
            List[str]: 更新メッセージリスト
        """
        if urls is None:
            self.logger.info("Check: Url is None.")
            results = [""]
        else:
            promises = [self._check_update(url) for url in urls]
            results = await asyncio.gather(*promises)
            results = list(itertools.chain.from_iterable(results))

            self.logger.info("Check: Success")
        return results

    def create_query(self, id: Any) -> str:
        """APIに与えるURLを作成

        Args:
            id (Any): ncode

        Returns:
            str: URL
        """
        return f"https://api.syosetu.com/writerblog/{id}.Atom"

    async def _check_update(self, url: Dict[str, Any]) -> List[str]:
        """更新チェック走査.

        Args:
            url (Dict[str, Any]): ncodeと最終更新日を記載した辞書データ

        Returns:
            str: 更新メッセージ
        """

        msgs = await self.request(url)

        # 更新があれば
        if len(msgs) > 0:
            self.logger.info(f"Check Success: {url[self.id]}")
        else:
            self.logger.error(f"Check Failed: {url[self.id]}")

        return msgs

    async def request(self, url: Dict[str, Any]) -> List[str]:
        """URLチェック.

        Args:
            url (Dict[str, Any]): ncodeと最終更新日を記載した辞書データ

        Returns:
            Tuple[datetime, str]: 最終更新日, タイトル(タイトルが空文字の場合は未更新とみなす)
        """
        msgs: List[str] = []

        try:
            userid = url[self.id]
            self.logger.info(f"Check: {userid}")
            address = self.create_query(userid)

            d = feedparser.parse(address)

            if d.bozo == 1:
                self.logger.error("Error: RSSの取得に失敗しました。")
                self.logger.error(d.bozo_exception)

                ret = str(d.bozo_exception)
                # await self.sendmessage(address + " の取得に失敗しました。" + ret)
                return msgs

            # 前回から更新されているか確認
            last_call = datetime.fromisoformat(url["lastupdated"])
            last_updated = datetime.fromtimestamp(
                mktime(d["updated_parsed"]) + 3600 * 9
            )

            if last_updated > last_call:
                self.logger.info(f"最終更新: {d['updated']} 更新があります")
                # 最終更新日時の更新
                url["lastupdated"] = last_updated.isoformat()
                for entries in reversed(d["entries"]):
                    update = datetime.fromtimestamp(
                        mktime(entries.updated_parsed) + 3600 * 9
                    )

                    # 前回更新以降の内容を出力
                    if update > last_call:
                        message = (
                            f"{entries['title']} "
                            + f"{entries['updated']} "
                            + f"{entries['link']}"
                        )
                        # await self.sendmessage(message)
                        # self.logger.info(message)
                        msgs.append(message)

            else:
                self.logger.info(f"最終更新: {d['updated']} 更新はありません")
            self.logger.info("checker success.")
        except AttributeError as e:
            message = "要素参照エラーが発生しました。エラーログを確認してください。"
            self.logger.exception(e)
        except Exception as e:
            message = "処理中に問題が発生しました。エラーログを確認してください。"
            self.logger.exception(e)
        return msgs
