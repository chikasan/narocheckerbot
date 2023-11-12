import asyncio
from datetime import datetime, timedelta
from logging import getLogger

import discord
from discord import Interaction, app_commands
from discord.errors import HTTPException
from discord.ext import commands, tasks

from narocheckerbot.config_manager import ConfigManager
from narocheckerbot.naro_api_gateway import NaroApiGateway
from narocheckerbot.naro_configuration import NaroConfigration


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

        self.config_manager = ConfigManager()
        self.checker_manager = NaroApiGateway()
        self.checker.start()

    async def cog_unload(self):
        """cog終了処理."""
        self.checker.cancel()

    async def sendmessage(self, message: str) -> None:
        """指定ちゃんねるにメッセージ送付.

        Args:
            message (str): 送付メッセージ
        """
        try:
            channel = self.bot.get_channel(self.config_manager.get_channel_id())
            if isinstance(channel, discord.TextChannel):
                await channel.send(message)
                # レートリミット対策
                await asyncio.sleep(1)
            else:
                self.logger.error("書き込みチャンネルが見つかりません")
        except discord.errors.Forbidden:
            self.logger.error("書き込み権限がありません。")
        pass

    @tasks.loop(seconds=3600)
    async def checker(self) -> None:
        """定期的に実行する処理."""
        await self.naro_update_check()

    async def naro_update_check(self) -> None:
        """更新チェックメイン処理."""
        self.logger.info("Check: Start")

        try:
            updated = False
            urls = self.config_manager.get_urls()
            results = await self.checker_manager.exec(urls)

            if results:
                for message in results:
                    if message:
                        updated = True
                        await self.sendmessage(message)

            if updated:
                # TODO: 更新に失敗したら書き込まれない。
                self.config_manager.write_yaml()
        except HTTPException:
            message = "レートリミットが発生しました。更新通知が正常に届かない可能性があります"
            self.logger.exception(message)
            # レートリミット発生中のため長めの待ち時間を設定
            await asyncio.sleep(3)
            await self.sendmessage(message)
        except AttributeError:
            message = "要素参照エラーが発生しました。エラーログを確認してください。"
            self.logger.exception(message)
            await self.sendmessage(message)
        except Exception:
            message = "処理中に問題が発生しました。エラーログを確認してください。"
            self.logger.exception(message)
            await self.sendmessage(message)

        self.logger.info("Check: Finish")

    @checker.before_loop
    async def before_checker(self):
        """更新チェック開始前に実施."""
        self.logger.info("waiting...")
        await self.bot.wait_until_ready()

        # 定期チェック開始まで時間がかかる場合があるため、起動直後にもチェックを実施
        await self.naro_update_check()

        # 更新の反映に最大5分かかるということで、予備で+2分設定。
        dt_now = datetime.now()
        dt2 = dt_now.replace(minute=7, second=0)

        if dt2 > dt_now:
            td = dt2 - dt_now
        else:
            td = dt2 - dt_now + timedelta(hours=1)

        self.logger.info(f"Wait time : {td.total_seconds()}")
        await asyncio.sleep(td.total_seconds())

    @app_commands.command()
    @app_commands.default_permissions()
    async def add(self, interaction: Interaction, ncode: str) -> None:
        """更新小説の追加コマンドです(Bot管理者のみ実行可能).

        Args:
            interaction (Interaction): インタラクション情報
            ncode (str): ncode
        """
        await interaction.response.defer()

        config = NaroConfigration(self.config_manager.get_urls())

        # 事前チェック(リストに登録済みかどうか確認)
        if config.is_exist_account(ncode=ncode):
            await interaction.followup.send(f"{ncode}はすでに登録されています.")
            return

        # 本チェック(登録できるか確認)
        url = {"lastupdated": datetime.now(), "ncode": ncode}
        (new_lastup, title) = await self.checker_manager.request(url)

        if len(title) > 0:
            url["lastupdated"] = new_lastup
            config.add(url)
            self.config_manager.write_yaml()

            self.logger.info(f"Add Success: {ncode}")
            await interaction.followup.send(f"{ncode}:{title}を追加しました")
        else:
            self.logger.error(f"Add Failed: {ncode}")
            await interaction.followup.send(f"登録に失敗しました。{ncode}が正しいものか確認してください。")

    @app_commands.command()
    @app_commands.default_permissions()
    async def delete(self, interaction: Interaction, ncode: str):
        """更新小説の削除コマンドです(Bot管理者のみ実行可能).

        Args:
            interaction (Interaction): インタラクション情報
            ncode (str): ncode
        """
        config = NaroConfigration(self.config_manager.get_urls())
        removed_value = config.delete(ncode)
        if removed_value:
            self.config_manager.write_yaml()
            self.logger.info(f"Delete Success: {removed_value['ncode']}")
            await interaction.response.send_message(f"{removed_value['ncode']}を削除しました")
        else:
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
