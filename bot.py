# -*- coding: utf-8 -*-
"""Bot起動モジュール."""

import os
from datetime import datetime
from logging import getLogger, StreamHandler, DEBUG, Formatter, Logger, FileHandler
from pathlib import Path

import discord
from discord.ext import commands


class NaroBot(commands.Bot):
    """Botクラス.

    Args:
        commands (commands.Bot): discordのBotクラス
    """

    def __init__(self, logger: Logger, intents: discord.Intents):
        """初期化.

        Args:
            logger (Logger): ロガーオブジェクト
            intents (discord.Intents): intentオブジェクト
        """
        super().__init__(command_prefix=[], intents=intents)
        self.logger = logger

    async def setup_hook(self):
        await self.load_extension("narocheckerbot.naro")

        await self.tree.sync()

    def run(self, token: str):
        """Botの起動処理.

        Args:
            token (str): DiscordBotのトークン
        """
        super().run(token)

    async def on_ready(self):
        """起動完了時に呼び出される処理."""
        self.logger.info("なろうBot起動しました")


if __name__ == "__main__":
    logger = getLogger("narocheckerlog")

    handler = StreamHandler()
    handler.setLevel(DEBUG)
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)

    logPath = Path("Logs")
    logPath.mkdir(exist_ok=True)

    file_handler = FileHandler(logPath / f"log{datetime.now():%Y%m%d%H%M%S}.log")
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(
        Formatter("%(asctime)s@ %(name)s [%(levelname)s] %(funcName)s: %(message)s")
    )
    logger.addHandler(file_handler)

    logger.propagate = False

    intents = discord.Intents.default()
    client = NaroBot(logger, intents)

    TOKEN = os.environ["NAROBOT_TOKEN"]

    client.run(TOKEN)
