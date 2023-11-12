import asyncio
from datetime import datetime
from logging import getLogger
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from ruamel.yaml import YAML

from narocheckerbot.webapi_gateway import WebApiGateway


class NaroApiGateway(WebApiGateway):
    """小説の更新確認を行う."""

    def __init__(self) -> None:
        """初期化."""
        self.logger = getLogger("narocheckerlog.naroapi")
        self.sem = asyncio.Semaphore(10)

        # 抽象化のための情報
        self.id = "ncode"

        pass

    async def exec(self, urls: Optional[List[Dict[Any, Any]]]) -> List[str]:
        """チェック処理本体.

        Args:
            urls (Optional[List[Dict[Any, Any]]]): ncodeと最終更新日を記載した辞書データ リスト
        """
        if urls is None:
            self.logger.info("Check: Url is None.")
            results = [""]
        else:
            promises = [self._check_update(url) for url in urls]
            results = await asyncio.gather(*promises)

            self.logger.info("Check: Success")
        return results

    def create_query(self, id: Any) -> str:
        """APIに与えるURLを作成

        Args:
            id (Any): ncode

        Returns:
            str: URL
        """
        return f"https://api.syosetu.com/novelapi/api/?ncode={id}&of=t-gl"

    async def _check_update(self, url: Dict[str, Any]) -> str:
        """更新チェック走査.

        Args:
            url (Dict[str, Any]): ncodeと最終更新日を記載した辞書データ
        """
        message = ""
        async with self.sem:
            (lastupdated, title) = await self.request(url)

        # 更新があれば
        if len(title) > 0:
            self.logger.info(f"Check Success: {url[self.id]}")
            if url["lastupdated"] != lastupdated:
                url["lastupdated"] = lastupdated

                page = f"https://ncode.syosetu.com/{url[self.id]}/"
                message = f"[更新] {title},{page}"
                self.logger.info(f"Update: {url[self.id]} {title}")
        else:
            message = f"Check Failed: {url[self.id]}"
            self.logger.error(message)

        return message

    async def request(self, url: Dict[str, Any]) -> Tuple[datetime, str]:
        """URLチェック.

        Args:
            url (Dict[str, Any]): ncodeと最終更新日を記載した辞書データ

        Returns:
            Tuple[datetime, str]: 最終更新日, タイトル
        """
        try:
            async with aiohttp.ClientSession() as session:
                ncode = url[self.id]
                self.logger.info(f"Check: {ncode}")
                address = self.create_query(ncode)
                # Todo : 存在チェックは可能?

                cnt = 0
                while cnt < 5:
                    # 関数化
                    try:
                        async with session.get(address) as r:
                            yaml = YAML()
                            result = yaml.load(await r.text())
                            if len(result) == 2:
                                return (result[1]["general_lastup"], result[1]["title"])
                            elif len(result) < 2:
                                self.logger.error(f"Not Found: {ncode} {cnt}")
                                break
                            else:
                                self.logger.error(f"Lots of candidates: {ncode} {cnt}")
                                break
                    except TypeError:
                        self.logger.error(f"Retry check: {ncode} {cnt}")
                        cnt = cnt + 1
                        await asyncio.sleep(60)
                    except IndexError:
                        self.logger.error(f"IndexError check: {ncode} {cnt}")
                        cnt = cnt + 1
                        await asyncio.sleep(60)
                    except OSError:
                        self.logger.exception(f"Timeout Semaphore: {ncode} {cnt}")
                        break
                if cnt >= 5:
                    self.logger.info(f"Timeout check: {ncode}")
        except TypeError as e:
            self.logger.exception(f"Error check: {e}")
        return (datetime.now(), "")

    pass
