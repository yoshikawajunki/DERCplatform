# DERCplatform

DERC実験で使用したDERCプラットフォームのシステムです。
このリポジトリ―を覗く方はDERCに有田・鈴木研究室の方だと思うので、DERCプラットフォームに関しては、2021年度に出した吉川純輝の修士論文「二層化ゲーミフィケーションに基づく間接互恵促進プラットフォームの提案」というタイトルで出しているので、読んでいただければと思います。そちらで説明しているため、使用方法についてはあまり触れずに、システム構成について述べていければと思います。

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
* SQlite3（上の本に使い方が載っています。以降、DBと呼びます。）
* Google Apps Script（以降、GASと呼びます。）
* Google Spread Sheet（以降、ssと呼びます。）
をメインで使用しました。

## 環境構築
- Python
Python(3.8.1)の実行環境を構築し、`pip install -r requirements.txt`  を実行して依存パッケージをダウンロードする

・GASの実行環境を整えるhttps://drive.google.com/drive/folders/1zCVqcMWUY0W2wT9kEX5VcTyeV3cTgOsD?usp=sharing。

- SSの準備
[https://drive.google.com/drive/folders/1VkuDIBmyC0hpdkgsLxQAsRJCBlKygicK] 以下の5つのスプレッドシートを自分の管理するGoogleDriveにコピーしておく

- PythonからGoogleSpreadSheetにアクセスするための準備
参考: [https://tanuhack.com/operate-spreadsheet/]

上のリンクを参考に以下の作業を行う
- アプリの作成
    - Google Drive APIの有効化
    - Google Sheets APIの有効化
- クレデンシャル情報の作成
    - 「サービスアカウント」からJSON形式で鍵を作成し、自分のPCにダウンロードしておく
- 上で用意した5つのスプレッドシートの共有フォームから、作成した鍵の中にあるメールアドレスを編集者として送信

- PythonとSlackを連携させるための準備
https://blog.imind.jp/entry/2020/03/07/231631
こちらのページを参考に準備する。Slackに投稿するためのbotを作成し、tokenを取得するところまで

- DB Browser for SQLiteをインストール（https://sqlitebrowser.org/）


## 実行する際の準備
### クレデンシャル情報の配置と読み込み

上記「PythonからGoogleSpreadSheetにアクセスするための準備」で作成したクレデンシャル鍵を `secret_key.json` と名前を付けてderc.pyと同じ階層のディレクトリに配置

### スプレッドシートのID設定
`[derc.py](http://derc.py)` 中にssのIDを記述する
コード内に、自分がコピーしたスプレッドシートのID(URL内の/d/以下の部分)を直書きする.

- SPREADSHEET_KEY_DB: ポイント管理+テキスト議論
- SPREADSHEET_KEY_slacklog_EvnetAPI: テキスト議論ログ倉庫
- SPREADSHEET_webdiscuss: ビデオ議論
- SPREADSHEET_hosuukeisan: ヘルスケア(歩数)
- SPREADSHEET_rita: 日常生活

### Slackのtoken設定
コード内に多数あるtoken指定部分すべてにtokenを指定(”Slackの連携の設定”で作成したslackbotのトークン)する。

### 実行
derc.pyを実行するとサーバが立ち上がるのでURLにアクセスする

### 全体概要
DERCプラットフォームは議論（ビデオ議論・テキスト議論）、日常生活、ヘルスケアの3つのアクティビティから構成されています。
それぞれのアクティビティのポイント計算システムは独立して動いており、使用するポイントのみ共有しています。基本的にWEBアプリ（Flask）はそのプログラムの中で、ページを見せたり、賭け情報の登録や、評価の登録などを行い、ポイント計算などにGASや、別のpythonファイルを使用しています。
以下、
* ポイントシステム
* バッヂシステム
* ビデオ議論
* テキスト議論
* 日常生活
* ヘルスケア
の詳しい説明を以下でしています。


### ポイントシステム
ポイントシステムはssに保存しています。各アクティビティの説明で詳しく行いますが、それぞれのアクティビティごとにポイント計算に使うツールが異なっています。異なるツールでそれぞれのアクティビティのポイントを計算して、ssに保存してある全体ポイントに反映しています。

開発当初はssのみで行っていましたが、ssのアクセス回数制限の壁にぶつかってしまい、アクセス回数の多いビデオ議論の記録はDBで行っています。正直DBの方が使い勝手がいいので今後はDBに統一していってもいいんじゃないかと思います。
議論、日常生活の成績発表はGASで行っています。GASで行っている理由はアクセス回数制限の壁と、ssを扱いやすいという事です。今後、DBにデータ保存を統一していくのならば、pythonファイルだけにまとめてもいいと思っています。

<img src="https://user-images.githubusercontent.com/91872741/154008942-0f686b87-7f8c-4e43-9405-4d1c6e18414a.png" width="500">

## バッヂシステム
獲得したポイントに応じてバッヂを付与しています。
ssに保存されているそれぞれのアクティビティの獲得ポイントをderc.dbにリアルタイムで同期させています（ss(ポイントシステム＋テキスト議論)のポイント管理タブの右側で、各アクティビティごとの獲得ポイント数が記録されています。）。
ユーザーがWEBアプリのページを踏むたびに、自分が今持っているバッヂの情報を取得するようになっています。バッヂの獲得条件を満たしたら、Slackで通知が行き、バッヂが付与されています。ssにはアクセス制限が設けれらており、たくさんssにアクセスすると回数制限の壁にぶつかっているので、ポイントシステムの情報だけはdbにコピーして、dbから情報を取得しています。アクセス制限が比較的シビアだということは開発の中盤に気づいたのでssを使用している部分が多くありますが、正直DBの方が使い勝手がいいので今後はDBに統一していってもいいんじゃないかと思います。
ssの情報をDBに反映させる方法は（@app.route('/UpdateDB', methods=['GET'])です。）を使用しています。見てみたらわかると思いますが、やり方を変えた方が良いと思います。

ここから
### ビデオ議論
ユーザー画面、derc.py、その他のツールで分けて説明を行います。図中の青色で囲まれたderc.pyの範囲は、プログラム内部のデコレーターを記述しています。
実際には、図よりももう少し複雑な仕組みになっています。例えば、「ユーザー画面」の賭け画面を表示するには、ssからデータを取って来なければいけないのですが、そこまで詳しく書くと逆に見にくくなりますし、難しい記述ではないので、図には入れていません。このように多くを省きました。
議論開始時間を設定し、1分ごとに稼働するGASが議論開始時間になった際に、議論の状況を議論前(ari)から議論中(playing)にして、議論が開始されます。
議論中、ssのアクセス回数を減らすために、評価はssとdeとdbの両方に記録して、自分の評価の回数はdbにて確認しています。
議論が終了したら、GASが結果の計算を行います。


<img src="https://user-images.githubusercontent.com/91872741/154044962-8a6c9363-da4d-4cb7-850a-e3e3cdfd769d.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/154044999-fe581370-abef-4141-9b22-c0229251d558.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/154044521-799dd95f-2e1b-4d47-8a08-5827f7855ba7.png" width="300">

### テキスト議論
大まかな流れはビデオ議論と変わりませんが、評価の仕組みは大きく異なります。
修士論文を見るとわかりますが、Slackで議論をして、そのログがリアルタイムでssに蓄積され、WEBアプリで見ることができるようになっています。

リアルタイムでログをssに保存するのはGASが行っています。こちらは
評価はビデオ議論では時間で記録していましたが、テキスト議論では投稿に対して評価を行っています。
議論開始、議論終了の仕組みはビデオ議論と変わりません。

<img src="https://user-images.githubusercontent.com/91872741/158050308-bec53cb7-caa4-4c3d-a047-6f3f41dcd909.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/158050321-fb37e045-3a2d-4097-87a1-4c07d9a4145c.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/158050331-170bd74d-8c27-4243-85c2-ea134bc51920.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/158050336-1dc19b99-61a7-4b2a-b2ac-5ab242da9e0e.png" width="300">


## 日常生活
議論に比べるとすっきりした仕組みです。賭けの方法は議論と変わりません。
利他行為されたことの記録はwebアプリのホームから行い、ssに保存されます。夜にGASが利他行為の回数や賭け情報から計算をして、その結果をSlackで報告し、ポイントシステムに反映させています。

<img src="https://user-images.githubusercontent.com/91872741/158050514-3a70262c-db03-4feb-9aec-db3efe79997f.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/158050529-3a164608-3021-49dd-a3f1-62810c6c2f4d.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/158050538-9d226955-c9b5-472d-adca-277bb3572422.png" width="300">



## ヘルスケア
<img src="https://user-images.githubusercontent.com/91872741/158050644-049c2e05-2027-4680-9430-f6c610e93899.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/158050653-739266e3-f5d4-4d43-8a1d-1729d72e340a.png" width="300">

被験者の歩数を取得する設定がだいぶめんどくさいです。設定方法は
[ココ](https://github.com/yoshikawajunki/getstepsystem)を参考にしてください。
ユーザーのスマートフォンやスマートウォッチから歩数を取得し、ssに保存するところまで書いてあります。
また、研究室内で歩数取得が引き継がれていれば、その担当の人に話を聞いてください（Googleのサービスは仕様変更が早いので、これを見ているときには使えなくなっている、もしくは設定の方法が変わっているかもしれません）。
getstepsystemのgetfit.pyでは歩数を取得して、ssに記録しているだけでしたが、このリポジトリのgetfit_derc.pyはその機能にプラスして賭け情報から賭け成功判定の追加などいろいろと追加してあると思います。歩数取得は、前日の歩数を取得するプログラムになっています。そして、結果の通知は23時にしていました。そのため、賭けは二日分記録されています。（前日中に賭けを行い、当日歩き、翌日結果発表がおこなれるため。）ssにも翌日分の賭け対象、翌々日分の賭け対象が記録されている部分があると思います。

歩数は前日分の歩数を発表するという特性上、賭け情報をssで二日分記録しておく必要があります。1日目に賭けるのは、二日目の歩数に対してですが、二日目の歩数の賭けの成功失敗判定は三日目に行われるからです。

<img src="https://user-images.githubusercontent.com/91872741/158050827-69f84188-e145-4a22-97ea-027d155d25b4.png" width="300">
<img src="https://user-images.githubusercontent.com/91872741/158050833-7f86e13c-de0b-465c-8220-d66f9b500b37.png" width="300">

