import os
from logging import getLogger

# import traceback
from typing import Dict, Any, Tuple
from datetime import datetime

import aiohttp
import asyncio
import discord
from discord.ext import tasks, commands
from discord import app_commands, Interaction
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
        try:
            channel = self.bot.get_channel(self.channel_id)
            if isinstance(channel, discord.TextChannel):
                await channel.send(message)
            else:
                self.logger.error("書き込みチャンネルが見つかりません")
        except discord.errors.Forbidden:
            self.logger.error("書き込み権限がありません。")
        pass

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
                self.logger.info(f"Check: {ncode}")
                address = f"https://api.syosetu.com/novelapi/api/?ncode={ncode}&of=t-gl"
                # Todo : 存在チェックは可能?

                cnt = 0
                while cnt < 5:
                    try:
                        async with session.get(address) as r:
                            result = yaml.safe_load(await r.text())
                            if len(result) == 2:
                                return (result[1]["general_lastup"], result[1]["title"])
                            elif len(result) < 2:
                                self.logger.error(f"Not Found: {ncode} {cnt}")
                                return (datetime.now(), "")
                            else:
                                self.logger.error(f"Lots of candidates: {ncode} {cnt}")
                                return (datetime.now(), "")
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
                self.logger.info(f"Timeout check: {ncode}")
                return (datetime.now(), "")
        except TypeError as e:
            self.logger.exception(f"Error check: {e}")
            # self.logger.info(traceback.format_exc())
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
            self.logger.error(message)
            await self.sendmessage(message)

    @tasks.loop(seconds=3600)
    async def checker(self) -> None:
        """更新チェック."""
        try:
            self.logger.info("Check: Start")

            urls = self.yaml_data["account"]
            if urls is None:
                self.logger.info("Check: Url is None.")
            else:
                promises = [self.fetch(url) for url in urls]
                await asyncio.gather(*promises)

            self.logger.info("Check: Finish")
        except AttributeError:
            message = "要素参照エラーが発生しました。エラーログを確認してください。"
            self.logger.exception(message)
            # self.logger.info(traceback.format_exc())
            await self.sendmessage(message)
        except Exception:
            message = "処理中に問題が発生しました。エラーログを確認してください。"
            self.logger.exception(message)
            # self.logger.info(traceback.format_exc())
            await self.sendmessage(message)

    @checker.before_loop
    async def before_checker(self):
        """更新チェック開始前に実施."""
        self.logger.info("waiting...")
        await self.bot.wait_until_ready()

    @app_commands.command()
    @app_commands.default_permissions()
    async def add(self, interaction: Interaction, ncode: str) -> None:
        """更新小説の追加コマンドです(Bot管理者のみ実行可能).

        Args:
            interaction (Interaction): インタラクション情報
            ncode (str): ncode
        """
        urls = self.yaml_data["account"]
        if urls is not None:
            for url in urls:
                if url["ncode"] == ncode:
                    await interaction.response.send_message(f"{ncode}はすでに登録されています.")
                    return
        else:
            self.yaml_data["account"] = []

        url = {"lastupdated": 0, "ncode": ncode}
        (new_lastup, title) = await self.check_update(url)

        if len(title) > 0:
            url["lastupdated"] = new_lastup

            self.yaml_data["account"].append(url)

            with open(self.configfile, "w") as stream:
                yaml.dump(self.yaml_data, stream=stream)

            self.logger.info(f"Add Success: {ncode}")
            await interaction.response.send_message(f"{ncode}を追加しました")
        else:
            self.logger.error(f"Add Failed: {ncode}")
            await interaction.response.send_message(
                f"登録に失敗しました。{ncode}が正しいものか確認してください。"
            )

    @app_commands.command()
    @app_commands.default_permissions()
    async def delete(self, interaction: Interaction, ncode: str):
        """更新小説の削除コマンドです(Bot管理者のみ実行可能).

        Args:
            interaction (Interaction): インタラクション情報
            ncode (str): ncode
        """
        for index, url in enumerate(self.yaml_data["account"]):
            if url["ncode"] == ncode:
                removed_value = self.yaml_data["account"].pop(index)
                with open(self.configfile, "w") as stream:
                    yaml.dump(self.yaml_data, stream=stream)
                self.logger.info(f"Delete Success: {removed_value['ncode']}")
                await interaction.response.send_message(
                    f"{removed_value['ncode']}を削除しました"
                )
                return

        self.logger.error(f"Delete Failed: {ncode}")
        await interaction.response.send_message("登録していない ncode です。")

    @app_commands.command()
    @app_commands.default_permissions()
    async def reload(self, interaction: Interaction):
        """Botの一部機能を再読込します(エラー時の再起動の代わりにまず実施することを想定).

        Args:
            interaction (Interaction): インタラクション情報
        """
        try:
            await self.bot.reload_extension("naro")
            self.logger.info("Reload.")
            await interaction.response.send_message("リロードしました")
        except Exception:
            self.logger.exception("Error: Reload Failed.")
            # self.logger.error(traceback.format_exc())
            await interaction.response.send_message("リロードに失敗しました。")
        pass


async def setup(bot: commands.Bot) -> None:
    """Cogの登録.

    Args:
        bot (commands.Bot): 参照するBotクラス
    """
    await bot.add_cog(NaroChecker(bot))
