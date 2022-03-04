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


### 全体概要（ポイントシステム）
DERCプラットフォームは議論（ビデオ議論・テキスト議論）、日常生活、ヘルスケアの3つのアクティビティから構成されています。
大まかな全体概要は以下の図のようになっていて、それぞれのアクティビティのポイントシステムは独立して動いています。基本的にWEBアプリ（Flask）はそのプログラムの中で、ページを見せたり、賭け情報の登録や、評価の登録などを行い、ポイント計算などにGASや、別のpythonファイルを使用しています。
以下、
* バッヂシステム
* ビデオ議論
* テキスト議論
* 日常生活
* ヘルスケア
の詳しい説明を以下でしています。

## 準備
pythonの実行環境を整える。僕はpythonの実行環境はanacondaを使用していました。
GASの実行環境を整える。
・pythonファイルからGoogleSpreadSheetにアクセスするために、準備が必要です。
https://tanuhack.com/operate-spreadsheet/
・pythonファイルからSlackに投稿するために、準備が必要です。
https://blog.imind.jp/entry/2020/03/07/231631
DB Browser for SQLiteをインストール（https://sqlitebrowser.org/）


### ファイルの説明
それぞれのファイルの説明を載せる。


### ポイントシステム
データの保存をssとDBで行っています。開発当初はssのみで行っていましたが、ssのアクセス回数制限の壁にぶつかってしまい、アクセス回数の多いビデオ議論の記録はDBで行っています。正直DBの方が使い勝手がいいので今後はDBに統一していってもいいんじゃないかと思います。
議論、日常生活の成績発表はGASで行っています。GASで行っている理由はアクセス回数制限の壁と、ssを扱いやすいという事です。今後、DBにデータ保存を統一していくのならば、pythonファイルだけにまとめてもいいと思っています。
<img src="https://user-images.githubusercontent.com/91872741/154008942-0f686b87-7f8c-4e43-9405-4d1c6e18414a.png" width="500">

## バッヂシステム
獲得したポイントに応じてバッヂを付与しています。
ss(ポイントシステム＋テキスト議論)のポイント管理タブの右側で、各アクティビティごとの獲得ポイント数が記録されています。
この情報は即座にDBに反映しています。（@app.route('/UpdateDB', methods=['GET'])です。）やり方を変えた方が良いと思います。
ユーザーがWEBアプリのページを踏むたびに、関数（getBadgeinfo）が呼び出されて、バッヂの獲得条件を満たしたら、Slackで通知が行き、バッヂが付与されています。

### ビデオ議論
ユーザー画面、derc.py、その他のツールで分けて説明を行います。derc.pyの範囲は、プログラム内部のデコレーターを記述しています。
実際には、図よりももう少し複雑な仕組みになっています。例えば、ユーザー画面の賭け画面を表示するには、ssからデータを取って来なければいけないのですが、そこまで詳しく書くと逆に見にくくなりますし、難しい記述ではないので、図には入れていません。このように多くを省きました。
<img src="https://user-images.githubusercontent.com/91872741/154044962-8a6c9363-da4d-4cb7-850a-e3e3cdfd769d.png" width="400">
<img src="https://user-images.githubusercontent.com/91872741/154044999-fe581370-abef-4141-9b22-c0229251d558.png" width="400">
<img src="https://user-images.githubusercontent.com/91872741/154044521-799dd95f-2e1b-4d47-8a08-5827f7855ba7.png" width="400">

### テキスト議論
大まかな流れはビデオ議論と変わりませんが、評価の仕組みは大きく異なります。
修士論文を見るとわかりますが、Slackで議論をして、そのログがリアルタイムでssに蓄積され、WEBアプリで見ることができるようになっています。
写真をはる

## 日常生活
議論に比べるとすっきりした仕組みです。

## 歩数
設定がだいぶめんどくさいです。設定方法は
[ココ](https://github.com/yoshikawajunki/getstepsystem)を参考にしてください。
ユーザーのスマートフォンやスマートウォッチから歩数を取得し、ssに保存するところまで書いてあります。
歩数取得は、前日の歩数を取得するプログラムになっています。そして、結果の通知は23時にしていました。そのため、賭けは二日分記録されています。（前日中に賭けを行い、当日歩き、翌日結果発表がおこなれるため。）ssにも翌日分の賭け対象、翌々日分の賭け対象が記録されている部分があると思います。


あと、画像を張り付けて、このgitにファイルをコピーして終了。
