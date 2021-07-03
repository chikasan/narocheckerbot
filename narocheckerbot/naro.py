import os
from logging import getLogger
import traceback
from typing import Dict, Any, Tuple
from datetime import datetime

import aiohttp
import asyncio
from discord.ext import commands, tasks
from ruamel import yaml


class NaroChecker(commands.Cog):
    """小説家になろう更新チェックBot.

    Args:
        commands (commands.Cog): 継承元
    """

    def __init__(self, bot: commands.Bot) -> None:
        """初期化.

        Args:
            bot ( (commands.Bot): 参照するBotクラス
        """
        super().__init__()
        self.bot = bot
        self.logger = getLogger("narocheckerlog.bot")
        self.configfile = os.path.dirname(os.path.abspath(__file__)) + "/config.yaml"
        with open(self.configfile, "r") as stream:
            self.yaml_data = yaml.safe_load(stream)
        self.channel_id = self.yaml_data["channel"]
        self.sem = asyncio.Semaphore(10)
        self.checker.start()

    def cog_unload(self):
        """cog終了処理."""
        self.checker.cancel()

    async def sendmessage(self, message: str) -> None:
        """指定ちゃんねるにメッセージ送付.

        Args:
            message (str): 送付メッセージ
        """
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(message)
        else:
            self.logger.info("書き込みチャンネルが見つかりません")

    async def check_update(self, url: Dict[str, Any]) -> Tuple[datetime, str]:
        """URLチェック.

        Args:
            url (Dict[str, Any]): ncodeと最終更新日を記載した辞書データ

        Returns:
            Tuple[datetime, str]: 最終更新日, タイトル
        """
        try:
            async with aiohttp.ClientSession() as session:
                ncode = url["ncode"]
                self.logger.info(f"check: {ncode}")
                address = f"https://api.syosetu.com/novelapi/api/?ncode={ncode}&of=t-gl"
                # Todo : 存在チェックは可能?

                cnt = 0
                while cnt < 5:
                    try:
                        async with session.get(address) as r:
                            result = yaml.safe_load(await r.text())[1]
                            return (result["general_lastup"], result["title"])
                    except TypeError:
                        self.logger.info(f"Retry check: {ncode} {cnt}")
                        cnt = cnt + 1
                        await asyncio.sleep(60)
                self.logger.info(f"Timeout check: {ncode}")
                return (datetime.now(), "")
        except TypeError as e:
            message = f"Error check: {e}"
            self.logger.info(message)
            self.logger.info(traceback.format_exc())
            return (datetime.now(), "")

    async def fetch(self, url: Dict[str, Any]) -> None:
        """更新チェック走査.

        Args:
            url (Dict[str, Any]): ncodeと最終更新日を記載した辞書データ
        """
        async with self.sem:
            (new_lastup, title) = await self.check_update(url)

        if len(title) > 0:
            self.logger.info(f"Check Success: {url['ncode']}")
            if url["lastupdated"] != new_lastup:
                url["lastupdated"] = new_lastup
                # タイトル
                page = f"https://ncode.syosetu.com/{url['ncode']}/"
                message = f"[更新] {title}  {page}"
                self.logger.info(message)
                await self.sendmessage(message)
                with open(self.configfile, "w") as stream:
                    yaml.dump(self.yaml_data, stream=stream)
                self.logger.info(f"Update: {url['ncode']} {title}")
        else:
            message = f"Check Failed: {url['ncode']}"
            self.logger.info(message)

    @tasks.loop(seconds=3600)
    async def checker(self) -> None:
        """更新チェック."""
        try:
            self.logger.info("Check: Start")
            promises = [self.fetch(url) for url in self.yaml_data["account"]]
            await asyncio.gather(*promises)
            self.logger.info("Check: Finish")
        except AttributeError:
            message = "要素参照エラーが発生しました。エラーログを確認してください。"
            self.logger.info(message)
            self.logger.info(traceback.format_exc())
            await self.sendmessage(message)
        except Exception:
            message = "処理中に問題が発生しました。エラーログを確認してください。"
            self.logger.info(message)
            self.logger.info(traceback.format_exc())
            await self.sendmessage(message)

    @checker.before_loop
    async def before_checker(self):
        """更新チェック開始前に実施."""
        self.logger.info("waiting...")
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.is_owner()
    async def add(self, ctx: commands.Context, ncode: str):
        """更新小説の追加コマンドです(Bot管理者のみ実行可能).

        Args:
            ctx (commands.Context): コンテキスト情報
            ncode (str): ncode
        """
        for url in self.yaml_data["account"]:
            if url["ncode"] == ncode:
                await ctx.send(f"{ncode}はすでに登録されています.")
                return

        url = {"lastupdated": 0, "ncode": ncode}
        (new_lastup, title) = await self.check_update(url)

        if len(title) > 0:
            url["lastupdated"] = new_lastup

            data = self.yaml_data["account"]
            data.append(url)

            with open(self.configfile, "w") as stream:
                yaml.dump(self.yaml_data, stream=stream)

            self.logger.info(f"Add Success: {ncode}")
            await ctx.send(f"{ncode}を追加しました")
        else:
            self.logger.info(f"Add Failed: {ncode}")
            await ctx.send("なろうAPIでアクセスできなかったので、追加しませんでした。")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context):
        """Botの一部機能を再読込します(エラー時の再起動の代わりにまず実施することを想定).

        Args:
            ctx (commands.Context): コンテキスト情報
        """
        try:
            self.bot.reload_extension("naro")
            self.logger.info("Reload.")
            await ctx.send("リロードしました")
        except Exception:
            self.logger.info("Error: Reload Failed.")
            self.logger.error(traceback.format_exc())
            await ctx.send("リロードに失敗しました。")


def setup(bot: commands.Bot) -> None:
    """Cogの登録.

    Args:
        bot (commands.Bot): 参照するBotクラス
    """
    bot.add_cog(NaroChecker(bot))
