# NaroCheckerbot

## 概要

小説家になろうを対象とした更新通知を行うDiscordBot

## 動作確認環境

* Windows
  * Windows11 64bit 24H2
  * Python : 3.11.12
  * discord.py 2.5.2
  * uv : 0.7.11
  * git : 2.49.0
* Raspberry Pi
  * Debian GNU/Linux 12 (bookworm) 64bit
  * Python : 3.11.2
  * discord.py 2.3.1
  * poetry : 1.6.1
  * git : 2.39.2

## 初期設定

1. pythonとuv, gitをあらかじめインストールしておく。
2. github上のファイルをダウンロードし、任意の位置に格納する。(git cloneでも可)
3. pyproject.tomlがあるディレクトリ上で下記を実行し、動作に必要なソフトウェアをインストールする。

   ```bash
   uv sync
   ```

4. sampleディレクトリにある。config.yamlをnarocheckerbot/narocheckerbotディレクトリにコピーする。
5. コピーしたconfig.yamlを開き、channel: 00000000000000000 の 00000000000000000 を更新を通知したいdiscordチャンネルのIDに書き換える。
6. 環境変数 NAROBOT_TOKEN を登録し、値として実際に使うBotのトークンを指定する。
   * Discord Botの権限
     * Scopes : bot と application.commands をチェック
     * Bot Permissions : Send Messages をチェック
   * 特権インテント
     * チェックしない。

## 起動方法

1. 下記コマンドを実行しBotを起動する。

   ```bash
   python3 bot.py
   ```

## スラッシュコマンド

* add
  * チェックする小説を追加
    * 追加した ncode と最終更新日を config.yaml に追記。
  * コマンド: /add {ncode}
    * 例: /add ncode:n5040ce
* delete
  * 小説のチェックを解除
    * 削除した ncode は config.yaml からも削除。
  * コマンド: /delete {ncode}
    * 例: /delete ncode:n5040ce

## ライセンス

MIT License
