# DERCplatform

DERC実験で使用したDERCプラットフォームのシステムです。
このリポジトリ―を覗く方はDERCに有田・鈴木研究室の方だと思うので、DERCプラットフォームに関しては、2021年度に出した吉川純輝の修士論文「二層化ゲーミフィケーションに基づく間接互恵促進プラットフォームの提案」というタイトルで出しているので、読んでいただければと思います。使用方法についてはあまり触れずに、システム構成について述べていければと思います。

### 主に使用しているツール
言語
* python
* javascript(GAS)
* HTML
* CSS

サービス
* flask
Pythonフレームワーク Flaskで学ぶWebアプリケーションのしくみとつくり方
[Amazonのリンク](https://www.amazon.co.jp/Python%E3%83%95%E3%83%AC%E3%83%BC%E3%83%A0%E3%83%AF%E3%83%BC%E3%82%AF-Flask%E3%81%A7%E5%AD%A6%E3%81%B6Web%E3%82%A2%E3%83%97%E3%83%AA%E3%82%B1%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AE%E3%81%97%E3%81%8F%E3%81%BF%E3%81%A8%E3%81%A4%E3%81%8F%E3%82%8A%E6%96%B9-%E6%8E%8C%E7%94%B0%E6%B4%A5%E8%80%B6%E4%B9%83/dp/4802612249)
を参考に作成しました。
* SQlite3（上の本に使い方が載っています。移行、DBと呼びます。）
* Google Apps Script（以降、GASと呼びます。）
* Google Spread Sheet（以降、ssと呼びます。）
をメインで使用しました。

### 全体概要
全体概要を載せる。
以下、
* あああ
* いいい
* ううう
に分けて説明を行っていきたいと思います。

### ファイルの説明
それぞれのファイルの説明を載せる。


### ポイントシステム
データの保存をssとDBで行っています。開発当初はssのみで行っていましたが、ssのアクセス回数制限の壁にぶつかってしまい、アクセス回数の多いビデオ議論の記録はDBで行っています。正直DBの方が使い勝手がいいので今後はDBに統一していってもいいんじゃないかと思います。
議論、日常生活の成績発表はGASで行っています。GASで行っている理由はアクセス回数制限の壁と、ssを扱いやすいという事です。今後、DBにデータ保存を統一していくのならば、pythonファイルだけにまとめてもいいと思っています。
<img src="https://user-images.githubusercontent.com/91872741/154008942-0f686b87-7f8c-4e43-9405-4d1c6e18414a.png" width="500">

### ビデオ議論
ユーザー画面、derc.py、その他のツールで分けて説明を行います。derc.pyの範囲は、プログラム内部のデコレーターを記述しています。
<img src="https://user-images.githubusercontent.com/91872741/154044962-8a6c9363-da4d-4cb7-850a-e3e3cdfd769d.png" width="500">
<img src="https://user-images.githubusercontent.com/91872741/154044999-fe581370-abef-4141-9b22-c0229251d558.png" width="500">
<img src="https://user-images.githubusercontent.com/91872741/154044521-799dd95f-2e1b-4d47-8a08-5827f7855ba7.png" width="500">
