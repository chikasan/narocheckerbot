# NaroCheckerbot

## 概要

小説家になろうを対象とした更新通知を行うDiscordBot

## 動作確認環境

* Windows
  * Windows10 64bit 21H1
  * Python : 3.9.5
  * discord.py : 1.7.3
  * poetry : 1.1.5
  * git : 2.27.0
* Raspberry Pi
  * Raspbian GNU/Linux 10 (buster)
  * Python : 3.9.5
  * discord.py : 1.7.3
  * poetry : 1.1.6
  * git : 2.20.1

## 初期設定

1. pythonとpoetry, gitをあらかじめインストールしておく。
2. github上のファイルをダウンロードする。(git cloneも可)
3. ダウンロードしたディレクトリ上で下記を実行し、動作に必要なソフトウェアをインストールする。

   ```
   poetry install --no-dev
   ```

4. sampleディレクトリにある。config.yamlをnarocheckerbotディレクトリにコピーする。
5. コピーしたconfig.yamlを開き、channel: 00000000000000000 の 00000000000000000 を更新を通知したいdiscordチャンネルのIDに書き換える。
6. 環境変数 NAROBOT_TOKEN を登録し、値として実際に使うBotのトークンを指定する。

## 起動方法

1. 下記コマンドを実行しBotを起動する。

   ```
   cd narocheckerbot
   python3 narocheckerbot.py
   ```

## コマンド

* add
  * チェックする小説を追加
    * 追加した ncode と最終更新日を config.yaml に追記。
  * コマンド: #add {ncode}
    * 例: #add n5040ce
* delete
  * 小説のチェックを解除
    * 削除した ncode は config.yaml からも削除。
  * コマンド: #delete {ncode}
    * 例: #delete n5040ce

## ライセンス

MIT License
