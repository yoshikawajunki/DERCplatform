#ssやGASなどはこちらのリンクから持ってきてください。https://drive.google.com/drive/folders/1zCVqcMWUY0W2wT9kEX5VcTyeV3cTgOsD?usp=sharing

from typing import Awaitable
import gspread
import json
import subprocess
import datetime
import schedule
import time
from slack_sdk import WebClient
from flask import Flask, flash, render_template, request, session, redirect, send_file, g
import numpy as np
from threading import Thread
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String#以下4文SQLAlchemyのためのimport
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound


###################スプレッドシート操作
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name('renkei_spreadsheet.json', scope)

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
#DB用
SPREADSHEET_KEY_DB = '設定してください'
#EventAPIでslackのログを保存しているスプレッドシート
SPREADSHEET_KEY_slacklog_EventAPI = '設定してください'
#共有設定したスプレッドシートを指定
#DB用
workbook_DB = gc.open_by_key(SPREADSHEET_KEY_DB)
#EventAPIでslackのログを保存しているスプレッドシート
workbook_slacklog_EventAPI = gc.open_by_key(SPREADSHEET_KEY_slacklog_EventAPI)
#ユーザー名からslackのアカウントIDを取ってくるためのシート
userIDchange = workbook_slacklog_EventAPI.worksheet('userIDchange')
#スプレッドシートの中のワークシート名を直接指定
worksheet1 = workbook_DB.worksheet('ポイント管理')
worksheet2 = workbook_DB.worksheet('チャンネル関連')
pointrireki = workbook_DB.worksheet('ポイント履歴')


#ビデオ会議関連のスプレッドシート
SPREADSHEET_webdiscuss = '設定してください'
workbook_webdiscuss = gc.open_by_key(SPREADSHEET_webdiscuss)
webchan = workbook_webdiscuss.worksheet('会議チャンネル関連')


#歩数計算のワークシート
SPREADSHEET_hosuukeisana = '設定してください'
SPREADSHEET_hosuukeisan = gc.open_by_key(SPREADSHEET_hosuukeisana)
hosuukeisan = SPREADSHEET_hosuukeisan.worksheet('歩数')


#日常生活のワークシート
SPREADSHEET_rita = '設定してください'
SPREADSHEET_rita = gc.open_by_key(SPREADSHEET_rita)
ritasheet = SPREADSHEET_rita.worksheet('利他行為')

###################スプレッドシート操作終わり

app = Flask(__name__)
app.secret_key = b'random string...'
engine = create_engine('sqlite:///derc.db',
connect_args={'check_same_thread': False}
)#SQLAlchemyのため
Base = declarative_base()#SQLAlchemyのため

all_user =["shimamoto","komori","shimaoka","hiramoto","asakura","banno","morinaga","sumitani","iwata","yamato","test"]
all_user_pswd=["lucas","afro","dark","gene","hero","riot","poruka","takemi","boss","tutida","aaa"]
all_user_ID =  ["slackの個人ID","slackの個人ID","X","","","","","","","",""]
chan_IDlist = ["slackのチャンネルID","slackのチャンネルID","","",""]

member_data = {}
message_data = []


# get Database Object.
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('derc.db', check_same_thread=False)
    return g.db


# close Dataabse Object.
def close_db(e=None):
    db = g.pop('db', None)


    if db is not None:
        db.close()


#下のDBのバッヂ情報を更新するための関数(def updateBadgeinfo(id))
def updateBadgeinfoDB(badgeinfo,id):    
    # model class
    class updateBadgeinfoclass(Base):
      __tablename__ = 'badgedata'
      __table_args__ = {'extend_existing': True}
      id = Column(Integer, primary_key=True)
      zentai_3000 = Column(Integer)
      zentai_6000 = Column(Integer)
      zentai_10000 = Column(Integer)
      zentai_15000 = Column(Integer)
      zentai_20000 = Column(Integer)
      zentai_30000 = Column(Integer)
      zentai_40000 = Column(Integer)
      zentai_50000 = Column(Integer)
      zentai_60000 = Column(Integer)
      discuss_dou = Column(Integer)
      discuss_gin = Column(Integer)
      discuss_kin = Column(Integer)
      discussLv1_dou = Column(Integer)
      discussLv1_gin = Column(Integer)
      discussLv1_kin = Column(Integer)
      discussLv2_dou = Column(Integer)
      discussLv2_gin = Column(Integer)
      discussLv2_kin = Column(Integer)
      hosuu_dou = Column(Integer)
      hosuu_gin = Column(Integer)
      hosuu_kin = Column(Integer)
      hosuuLv1_dou = Column(Integer)
      hosuuLv1_gin = Column(Integer)
      hosuuLv1_kin = Column(Integer)
      hosuuLv2_dou = Column(Integer)
      hosuuLv2_gin = Column(Integer)
      hosuuLv2_kin = Column(Integer)
      ritakoui_dou = Column(Integer)
      ritakoui_gin = Column(Integer)
      ritakoui_kin = Column(Integer)
      ritakouiLv1_dou = Column(Integer)
      ritakouiLv1_gin = Column(Integer)
      ritakouiLv1_kin = Column(Integer)
      ritakouiLv2_dou = Column(Integer)
      ritakouiLv2_gin = Column(Integer)
      ritakouiLv2_kin = Column(Integer)

    Session = sessionmaker(bind = engine)
    ses = Session()
    mydata = ses.query(updateBadgeinfoclass).filter(updateBadgeinfoclass.id == id).one()
    exec_code = 'mydata.' + badgeinfo + '= 1' 
    exec(exec_code)
    ses.add(mydata)
    ses.commit()
    ses.close()

#バッヂの更新情報をSlackで通知する。
def badgeinfotuuti(user_id):
    #評価を通知するプログラム始まり
    token = "設定してください"#ワークスペース名前
    client = WebClient(token)
    #自分のuserID取ってくる
    user_id = all_user_ID[user_id]#自分のslackのIDを取ってくる。
    # DMを開き，channelidを取得する．
    res = client.conversations_open(users=user_id)
    dm_id = res['channel']['id']

    # DMを送信する
    client.chat_postMessage(channel=dm_id, text= "新しいバッヂをゲットしました！")
    #評価を通知するプログラム終わり

#バッヂの情報を更新してSlackで通知する関数
#上の関数を以下の関数内で読み込んでいるよ。
def updateBadgeinfo(id):
    badgedatatwo = []
    badgedata = []
    db = get_db()
    cur_badge = db.execute("select * from badgedata where id = {id}".format(id = id))
    badgedatatwo = cur_badge.fetchall()
    for ooo in range(50):#DBから取ってきたままだと2次元で扱いにくいため一次元に返還する。
        badgedata.append(badgedatatwo[0][ooo])
    #以下それぞれの獲得ポイントを格納する。
    receivePt_zentai = badgedata[2]
    receivePt_discuss = badgedata[3]
    receivePt_discussLv1 = badgedata[4]
    receivePt_discussLv2 = badgedata[5]
    receivePt_hosuu = badgedata[6]  
    receivePt_hosuuLv1 = badgedata[7]
    receivePt_hosuuLv2 = badgedata[8]
    receivePt_ritakoui = badgedata[9]
    receivePt_ritakouiLv1 = badgedata[10]
    receivePt_ritakouiLv2 = badgedata[11]
    del badgedata[:12]#名前とかidとか各アクティビティで取得したポイントとかの情報を削除する。

    ##バッヂの色は銅はほぼ全員が到達した、銀は半分が到達した、金は3人が到達した。という判定で
    #全体ポイントのバッヂの更新
    if receivePt_zentai >= 3000 and badgedata[0] == 0: 
        updateBadgeinfoDB("zentai_3000",id)
        badgeinfotuuti(id -1)
    
    if receivePt_zentai >= 6000 and badgedata[1] == 0: 
        updateBadgeinfoDB("zentai_6000",id)
        badgeinfotuuti(id -1)
    
    if receivePt_zentai >= 10000 and badgedata[2] == 0: 
        updateBadgeinfoDB("zentai_10000",id)
        badgeinfotuuti(id -1)
    
    if receivePt_zentai >= 15000 and badgedata[3] == 0: 
        updateBadgeinfoDB("zentai_15000",id)
        badgeinfotuuti(id -1)
    
    if receivePt_zentai >= 20000 and badgedata[4] == 0: 
        updateBadgeinfoDB("zentai_20000",id)
        badgeinfotuuti(id -1)
    
    if receivePt_zentai >= 30000 and badgedata[5] == 0: 
        updateBadgeinfoDB("zentai_30000",id)
        badgeinfotuuti(id -1)
    
    if receivePt_zentai >= 40000 and badgedata[6] == 0: 
        updateBadgeinfoDB("zentai_40000",id)
        badgeinfotuuti(id -1)
    
    if receivePt_zentai >= 50000 and badgedata[7] == 0: 
        updateBadgeinfoDB("zentai_50000",id)
        badgeinfotuuti(id -1)

    if receivePt_zentai >= 60000 and badgedata[8] == 0: 
        updateBadgeinfoDB("zentai_60000",id)
        badgeinfotuuti(id -1)

    del badgedata[:9]#全体ポイントのバッヂ情報を消去
    
    #議論全体ポイントのバッヂの更新3000,7000,12000
    if receivePt_discuss >= 3000 and badgedata[0] == 0: 
        updateBadgeinfoDB("discuss_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_discuss >= 7000 and badgedata[1] == 0: 
        updateBadgeinfoDB("discuss_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_discuss >= 12000 and badgedata[2] == 0: 
        updateBadgeinfoDB("discuss_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#議論全体ポイントのバッヂ情報を消去

    #議論Lv1ポイントのバッヂの更新2000,5000,8000
    if receivePt_discussLv1 >= 2000 and badgedata[0] == 0: 
        updateBadgeinfoDB("discussLv1_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_discussLv1 >= 5000 and badgedata[1] == 0: 
        updateBadgeinfoDB("discussLv1_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_discussLv1 >= 10000 and badgedata[2] == 0: 
        updateBadgeinfoDB("discussLv1_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#議論Lv1ポイントのバッヂ情報を消去

    #議論Lv2ポイントのバッヂの更新5000,10000,15000
    if receivePt_discussLv2 >= 6000 and badgedata[0] == 0: 
        updateBadgeinfoDB("discussLv2_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_discussLv2 >= 12000 and badgedata[1] == 0: 
        updateBadgeinfoDB("discussLv2_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_discussLv2 >= 25000 and badgedata[2] == 0: 
        updateBadgeinfoDB("discussLv2_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#議論Lv2ポイントのバッヂ情報を消去

    #歩数全体ポイントのバッヂの更新5000,10000,20000
    if receivePt_hosuu >= 5000 and badgedata[0] == 0: 
        updateBadgeinfoDB("hosuu_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_hosuu >= 10000 and badgedata[1] == 0: 
        updateBadgeinfoDB("hosuu_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_hosuu >= 20000 and badgedata[2] == 0: 
        updateBadgeinfoDB("hosuu_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#歩数全体ポイントのバッヂ情報を消去

    #歩数Lv1ポイントのバッヂの更新5000,15000,25000
    if receivePt_hosuuLv1 >= 5000 and badgedata[0] == 0: 
        updateBadgeinfoDB("hosuuLv1_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_hosuuLv1 >= 15000 and badgedata[1] == 0: 
        updateBadgeinfoDB("hosuuLv1_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_hosuuLv1 >= 25000 and badgedata[2] == 0: 
        updateBadgeinfoDB("hosuuLv1_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#歩数Lv1ポイントのバッヂ情報を消去

    #歩数Lv2ポイントのバッヂの更新3000,7000,10000
    if receivePt_hosuuLv2 >= 3000 and badgedata[0] == 0: 
        updateBadgeinfoDB("hosuuLv2_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_hosuuLv2 >= 7000 and badgedata[1] == 0: 
        updateBadgeinfoDB("hosuuLv2_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_hosuuLv2 >= 10000 and badgedata[2] == 0: 
        updateBadgeinfoDB("hosuuLv2_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#歩数LLv2全体ポイントのバッヂ情報を消去

    #利他行為全体ポイントのバッヂの更新1000,2500,4000
    if receivePt_ritakoui >= 1000 and badgedata[0] == 0: 
        updateBadgeinfoDB("ritakoui_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_ritakoui >= 2500 and badgedata[1] == 0: 
        updateBadgeinfoDB("ritakoui_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_ritakoui >= 4000 and badgedata[2] == 0: 
        updateBadgeinfoDB("ritakoui_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#利他行為全体ポイントのバッヂ情報を消去

    #利他行為Lv1ポイントのバッヂの更新500,1500,3000
    if receivePt_ritakouiLv1 >= 500 and badgedata[0] == 0: 
        updateBadgeinfoDB("ritakouiLv1_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_ritakouiLv1 >= 1500 and badgedata[1] == 0: 
        updateBadgeinfoDB("ritakouiLv1_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_ritakouiLv1 >= 3000 and badgedata[2] == 0: 
        updateBadgeinfoDB("ritakouiLv1_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#利他行為Lv1ポイントのバッヂ情報を消去

    #利他行為Lv2ポイントのバッヂの更新500,1500,3000
    if receivePt_ritakouiLv2 >= 500 and badgedata[0] == 0: 
        updateBadgeinfoDB("ritakouiLv2_dou",id)
        badgeinfotuuti(id -1)
    
    if receivePt_ritakouiLv2 >= 1500 and badgedata[1] == 0: 
        updateBadgeinfoDB("ritakouiLv2_gin",id)
        badgeinfotuuti(id -1)

    if receivePt_ritakouiLv2 >= 3000 and badgedata[2] == 0: 
        updateBadgeinfoDB("ritakouiLv2_kin",id)
        badgeinfotuuti(id -1)

    del badgedata[:3]#利他行為Lv2ポイントのバッヂ情報を消去
    

#バッヂの状態を取得する関数
#ゆくゆくは取得して、ポイントに応じてバッヂの状態も更新する関数にしたい。
def getBadgeinfo(id):
    badgedatatwo = []
    badgedata = []
    db = get_db()
    cur_badge = db.execute("select * from badgedata where id = {id}".format(id = id))
    badgedatatwo = cur_badge.fetchall()
    for ooo in range(50):#DBから取ってきたままだと2次元で扱いにくいため一次元に返還する。
        badgedata.append(badgedatatwo[0][ooo])
    del badgedata[:12]#名前とかidとか各アクティビティで取得したポイントとかの情報を削除する。

    if badgedata[8] =="1":#全体ポイントのバッヂの色判定
        zentai = "60000"
    elif badgedata[7] == 1:
        zentai = "50000"
    elif badgedata[6] == 1:
        zentai = "40000"
    elif badgedata[5] == 1:
        zentai = "30000"
    elif badgedata[4] == 1:
        zentai = "20000"
    elif badgedata[3] == 1:
        zentai = "15000"
    elif badgedata[2] == 1:
        zentai = "10000"
    elif badgedata[1] == 1:
        zentai = "6000"
    elif badgedata[0] == 1:
        zentai = "3000"
    else:
        zentai = "nasi"
    del badgedata[:9]#全体ポイントの情報を削除

    if badgedata[2] ==1:#議論のバッヂの色判定
        discuss = "kin"
    elif badgedata[1] ==1:
        discuss = "gin"
    elif badgedata[0] ==1:
        discuss = "dou"
    else:
        discuss = "nasi"
    del badgedata[:3]#議論の情報を削除

    if badgedata[2] ==1:#議論Lv1のバッヂの色判定
        discussLv1 = "kin"
    elif badgedata[1] ==1:
        discussLv1 = "gin"
    elif badgedata[0] ==1:
        discussLv1 = "dou"
    else:
        discussLv1 = "nasi"
    del badgedata[:3]#議Lv1の情報を削除

    if badgedata[2] ==1:#議論Lv2のバッヂの色判定
        discussLv2 = "kin"
    elif badgedata[1] ==1:
        discussLv2 = "gin"
    elif badgedata[0] ==1:
        discussLv2 = "dou"
    else:
        discussLv2 = "nasi"
    del badgedata[:3]#議論Lv2の情報を削除

    if badgedata[2] ==1:#歩数のバッヂの色判定
        hosuu = "kin"
    elif badgedata[1] ==1:
        hosuu = "gin"
    elif badgedata[0] ==1:
        hosuu = "dou"
    else:
        hosuu = "nasi"
    del badgedata[:3]#歩数の情報を削除

    if badgedata[2] ==1:#歩数Lv1のバッヂの色判定
        hosuuLv1 = "kin"
    elif badgedata[1] ==1:
        hosuuLv1 = "gin"
    elif badgedata[0] ==1:
        hosuuLv1 = "dou"
    else:
        hosuuLv1 = "nasi"
    del badgedata[:3]#歩数Lv1の情報を削除

    if badgedata[2] ==1:#歩数Lv2のバッヂの色判定
        hosuuLv2 = "kin"
    elif badgedata[1] ==1:
        hosuuLv2 = "gin"
    elif badgedata[0] ==1:
        hosuuLv2 = "dou"
    else:
        hosuuLv2 = "nasi"
    del badgedata[:3]#歩数Lv2の情報を削除

    if badgedata[2] ==1:#利他行為のバッヂの色判定
        ritakoui = "kin"
    elif badgedata[1] ==1:
        ritakoui = "gin"
    elif badgedata[0] ==1:
        ritakoui = "dou"
    else:
        ritakoui = "nasi"
    del badgedata[:3]#利他行為の情報を削除

    if badgedata[2] ==1:#利他行為Lv1のバッヂの色判定
        ritakouiLv1 = "kin"
    elif badgedata[1] ==1:
        ritakouiLv1 = "gin"
    elif badgedata[0] ==1:
        ritakouiLv1 = "dou"
    else:
        ritakouiLv1 = "nasi"
    del badgedata[:3]#利他行為Lv1の情報を削除

    if badgedata[2] ==1:#利他行為Lv2のバッヂの色判定
        ritakouiLv2 = "kin"
    elif badgedata[1] ==1:
        ritakouiLv2 = "gin"
    elif badgedata[0] ==1:
        ritakouiLv2 = "dou"
    else:
        ritakouiLv2 = "nasi"
    del badgedata[:3]#利他行為Lv2の情報を削除


    return(zentai,discuss,discussLv1,discussLv2,hosuu,hosuuLv1,hosuuLv2,ritakoui,ritakouiLv1,ritakouiLv2)


###DB扱うコードの例始まり##################################################

# model class（mydata用）
class Mydata(Base):
    __tablename__ = 'mydata'
    __table_args__ = {'extend_existing': True}
 
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    mail = Column(String(255))
    tosi = Column(Integer)


    # get Dict data
    def toDict(self):
        return {
            'id':int(self.id), 
            'name':str(self.name), 
            'mail':str(self.mail), 
            'age':int(self.age)
        }

#DBへの書き込みの例(上のmodel classもいるよ)
@app.route('/sample2aaa', methods=['GET'])
def sample2aaa():
    name = "ccc"
    mail = "ddd"
    age = "33"
    id = 12
    Session = sessionmaker(bind = engine)
    ses = Session()
    mydata = ses.query(Mydata).filter(Mydata.id == id).one()
    mydata.name = name
    mydata.mail = mail
    mydata.age = int(age)
    ses.add(mydata)
    ses.commit()
    ses.close()
    return render_template('sample.html', 
        title='Index', 
        message='※SQLite3 Databaseaaa',
        alert='This is SQLite3 Database Sample!',
        )

#DBからの読み取りの例
@app.route('/sample', methods=['GET'])
def sample():
    mydata = []
    db = get_db()
    testtesttest = 4
    cur = db.execute("select * from mydata where id = {testtesttest}".format(testtesttest = testtesttest))
    mydata = cur.fetchall()
    return render_template('sample.html', 
        title='Index', 
        message='※SQLite3 Database',
        alert='This is SQLite3 Database Sample!',
        data=mydata)

###DB扱うコードの例終わり##################################################

#ホームページ
@app.route('/', methods=['GET'])
def Home():
    
    if 'login' in session and session['login']:
        name = session['name']
        user_info = session['user_info']
        points = int(user_info[4])#自分のポイント数を取得
        tomorrowpoints = points * 85 // 100

        persons = []
        for i in range(len(all_user)):
          persons.append([all_user[i]])

        mNumber = all_user.index(name)#被利他行為選択ページで自分の名前を表示させない。
        persons.pop(mNumber)
        
        id = session['id']
        updateBadgeinfo(id)
        UpdateDB()
        Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

        return render_template('Home.html',
        title = 'Welcome!',
        zentai = Badgeinfo[0],
        discuss = Badgeinfo[1],
        discussLv1 = Badgeinfo[2],
        discussLv2 = Badgeinfo[3],
        hosuu = Badgeinfo[4],
        hosuuLv1 = Badgeinfo[5],
        hosuuLv2 = Badgeinfo[6],
        ritakoui = Badgeinfo[7],
        ritakouiLv1 = Badgeinfo[8],
        ritakouiLv2 = Badgeinfo[9],
        err=False,
        persons = persons,
        name=name ,
        tomorrowpoints = tomorrowpoints,
        points = points)

    else:
        return redirect('/Login')

@app.route('/', methods=['POST'])
def Home_post():
    name = session['name']
    ritaname = request.form.get('ritaperson')
    message = request.form.get('message')

    ritasheetrowlength =1 + len(ritasheet.col_values(1) )#行の長さを取得する。
    ritasheet.update_cell(ritasheetrowlength, 3, name)################################################書き込み
    ritasheet.update_cell(ritasheetrowlength, 4, ritaname)################################################書き込み
    ritasheet.update_cell(ritasheetrowlength, 5, message)################################################書き込み
    ritasheet.update_cell(ritasheetrowlength, 1, "あ")################################################書き込み

    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
    return render_template('Thankyourita.html',
        zentai = Badgeinfo[0],
        discuss = Badgeinfo[1],
        discussLv1 = Badgeinfo[2],
        discussLv2 = Badgeinfo[3],
        hosuu = Badgeinfo[4],
        hosuuLv1 = Badgeinfo[5],
        hosuuLv2 = Badgeinfo[6],
        ritakoui = Badgeinfo[7],
        ritakouiLv1 = Badgeinfo[8],
        ritakouiLv2 = Badgeinfo[9],
        title='Thank you!!',
        name = name,
        err=False)

#point_history、ポイント履歴確認ページ
@app.route('/point_history', methods=['GET'])
def point_history():
    name = session['name']
    user_num = all_user.index(name)#自分の名前をログでとってくる。
    all_pointrireki = np.array(pointrireki.get_all_values())#ポイント履歴の全てのログを持ってくる。##############################################
    date_list = all_pointrireki[1]#日付を取ってくる。
    point_list = all_pointrireki[user_num + 2]
    rireki = []
    for i in range(point_list.size - 2):#最初の二つを取って来ないようにするため。
        rireki.append([date_list[point_list.size - (i+1)], point_list[point_list.size - (i+1)]])#2つの一次元配列を足し合わせて二次元配列にする。
    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
    return render_template('point_history.html',
            title='ポイント履歴',
            zentai = Badgeinfo[0],
            discuss = Badgeinfo[1],
            discussLv1 = Badgeinfo[2],
            discussLv2 = Badgeinfo[3],
            hosuu = Badgeinfo[4],
            hosuuLv1 = Badgeinfo[5],
            hosuuLv2 = Badgeinfo[6],
            ritakoui = Badgeinfo[7],
            ritakouiLv1 = Badgeinfo[8],
            ritakouiLv2 = Badgeinfo[9],
            pointsrireki = rireki,
            name = name,
            err=False,)

#ログインページ
@app.route('/Login', methods=['GET'])
def Login():
    return render_template('Login.html',
            title='Login page',
            err=False,)
            
#入力された名前とpasswordがスプレッドシートと合致していたらログインできる。
@app.route('/Login', methods=['POST'])
def login_post():
    Number = 1
    global member_data
    name = request.form.get('name')
    pswd = request.form.get('pass')
    
    if name in all_user:
      namenum = all_user.index(name)
    
    else:
        return render_template('Login.html',
            title='Login page',
            err=False)



    user_info = worksheet1.row_values(namenum + 3)  #user_listにシート1からユーザーの情報を一次元配列で取得。############################################################
    if pswd ==all_user_pswd[namenum]:#入力されたパスワードがあっているか確認（user_listのなかにあるか確認）
        session['login'] = True
    else:
        session['login'] = False

    session['name'] = name #nameを全ページで保存する。
    session['user_info'] = user_info #user_infoを全ページで保存する。
    session['id'] = all_user.index(name) + 1#DB取得の貯めに必要なidを保存。


    if session['login']:
        return redirect('/')
    else:
        return render_template('Login.html',
            title='Login page',
            err=False)


#議論方式選択ページ
@app.route('/discussHome', methods=['GET'])
def discussHome():
    name = session['name']
    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
    return render_template('discussHome.html',
            title='Choice of discussion method',
            zentai = Badgeinfo[0],
            discuss = Badgeinfo[1],
            discussLv1 = Badgeinfo[2],
            discussLv2 = Badgeinfo[3],
            hosuu = Badgeinfo[4],
            hosuuLv1 = Badgeinfo[5],
            hosuuLv2 = Badgeinfo[6],
            ritakoui = Badgeinfo[7],
            ritakouiLv1 = Badgeinfo[8],
            ritakouiLv2 = Badgeinfo[9],
            name = name,
            err=False)

#####################################################################################################chat議論のページ始まり#####################################################################################################

#テキスト議論選択ページ
@app.route('/Channelselection_Chat', methods=['GET'])
def Channelselection_Chat():
    name = session['name']
    all_worksheet2 = np.array(worksheet2.get_all_values())#worksheet2の全てのログを持ってくる。################################################
    chan_list = all_worksheet2[:, 1]#シート2のチャンネルリストをとってくる。
    chan_info = all_worksheet2[:, 2]#チャンネルの議論の情報を取ってくる。
    chan_info_a = []#上のari,nasi,playingをDERC設定あり、DERC設定なし、DERCでの議論進行中、に変える。
    for i in range(len(chan_list)):
        if chan_info[i] == "ari":
            chan_info_a.append("ゲーム設定あり")

        elif chan_info[i] == "nasi":
            chan_info_a.append("ゲーム設定なし")

        elif chan_info[i] == "playing":
            chan_info_a.append("ゲーム進行中")

        else:
            chan_info_a.append("エラー")

    chan_a = []#チャンネル名とチャンネル情報を合わせた二次元配列
    for j in range(len(chan_list)):
        if chan_list[j] =="" :
            break
        else:
            chan_a.append([chan_list[j], chan_info_a[j]])
    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
    
    return render_template('Channelselection_Chat.html',
            name = name,
            zentai = Badgeinfo[0],
            discuss = Badgeinfo[1],
            discussLv1 = Badgeinfo[2],
            discussLv2 = Badgeinfo[3],
            hosuu = Badgeinfo[4],
            hosuuLv1 = Badgeinfo[5],
            hosuuLv2 = Badgeinfo[6],
            ritakoui = Badgeinfo[7],
            ritakouiLv1 = Badgeinfo[8],
            ritakouiLv2 = Badgeinfo[9],
            title='Channel selection(Chat)',
            chan_list = chan_a)


#テキスト議論を選択したら、各議論の状態のページに行くことができる（議論中→評価ページ、議論前→賭けページ、など）
@app.route('/ChannelSetting_Chat/<channel>', methods=['GET'])
def ChannelSetting_Chat(channel):
    name = session['name']
    Number = 0
    all_worksheet2 = np.array(worksheet2.get_all_values())#worksheet2の全てのログを持ってくる。################################################
    chan_list = all_worksheet2[:, 1]#シート2のチャンネルリストをとってくる。
    # 注意！！クエリパラメーターのchannelをそのまま持ってくると、channelには実は"BBQ日程決め"などの本当に得たいものと"site.webmanifest"というものも入ることがわかったので、"site.webmanifest"を除外している。
    if channel != "site.webmanifest":
        chan = channel
        for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
            if i != chan:
                Number += 1
            elif i == chan:
                break

    chanNumber = 1
    for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
        if i != channel:
            chanNumber += 1
        elif i == channel:
            break
    session['chanNumber'] = chanNumber

    chan_list_PorA = chan_info = all_worksheet2[:, 2]  # シート2からチャンネルがDERC設定が有か無しかを取得（Presence or Absence→PorA）。
    session['Number'] = Number
    if chan_list_PorA[Number] == "ari":
        session['channel'] = channel
        return redirect('/kake_chat')  #kake_chatへ

    elif chan_list_PorA[Number] == "playing":
        session['playingchannel'] = channel
        return redirect('/Discussing_Chat')  # 議論が始まっているのでDiscussing_Chatへ

    elif chan_list_PorA[Number] == "nasi":
        session['channel'] = channel
        return redirect('/settingchat')


#議論情報「nasi」から飛んできた場合、議論を設定できる
@app.route('/settingchat', methods=['GET'])
def settingchat():
    channel = session['channel']
    name = session['name']
    Number = 0
    all_worksheet2 = np.array(worksheet2.get_all_values())#worksheet2の全てのログを持ってくる。################################################
    chan_list = all_worksheet2[:, 1]#シート2のチャンネルリストをとってくる。
    # 注意！！クエリパラメーターのchannelをそのまま持ってくると、channelには実は"BBQ日程決め"などの本当に得たいものと"site.webmanifest"というものも入ることがわかったので、"site.webmanifest"を除外している。
    if channel != "site.webmanifest":
        chan = channel
        for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
            if i != chan:
                Number += 1
            elif i == chan:
                break
    chan_list = all_worksheet2[:, 1]#シート2のチャンネルリストをとってくる。
    chanNumber = 1
    for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
        if i != channel:
            chanNumber += 1
        elif i == channel:
            break

    chan_list_PorA = chan_info = all_worksheet2[:, 2]  # シート2からチャンネルがDERC設定が有か無しかを取得（Presence or Absence→PorA）。
    session['Number'] = Number
    starttimestr = all_worksheet2[chanNumber - 1][3]
    finishtimestr= all_worksheet2[chanNumber - 1][4]

    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    if len(starttimestr) != 0:
        return render_template('ChannelSetting_Chat.html',
        arinasi = "の議論の設定",
        title='Setting',
        zentai = Badgeinfo[0],
        discuss = Badgeinfo[1],
        discussLv1 = Badgeinfo[2],
        discussLv2 = Badgeinfo[3],
        hosuu = Badgeinfo[4],
        hosuuLv1 = Badgeinfo[5],
        hosuuLv2 = Badgeinfo[6],
        ritakoui = Badgeinfo[7],
        ritakouiLv1 = Badgeinfo[8],
        ritakouiLv2 = Badgeinfo[9],
        zyoukyou1 ="既に",
        start = starttimestr,
        finish = finishtimestr,
        zyoukyou2 = "に設定されています",
        name = name,
        channel=channel)

    else:
        return render_template('ChannelSetting_Chat.html',
        zentai = Badgeinfo[0],
        discuss = Badgeinfo[1],
        discussLv1 = Badgeinfo[2],
        discussLv2 = Badgeinfo[3],
        hosuu = Badgeinfo[4],
        hosuuLv1 = Badgeinfo[5],
        hosuuLv2 = Badgeinfo[6],
        ritakoui = Badgeinfo[7],
        ritakouiLv1 = Badgeinfo[8],
        ritakouiLv2 = Badgeinfo[9],
        arinasi = "の議論の設定",
        title='Setting',
        name = name,
        channel=channel)

@app.route('/settingchat', methods=['POST'])
def settingchatPOST():
    discussionstartdate = request.form.get('discussionstartdate')#開始
    discussionstarttime = request.form.get('discussionstarttime')
    discussionfinishdate = request.form.get('discussionfinishdate')#終了
    discussionfinishtime = request.form.get('discussionfinishtime')
    Number = session['Number']
    zikangime = Number +1
    discussionstart = discussionstartdate +" " +discussionstarttime
    discussionfinish = discussionfinishdate +" " +discussionfinishtime
    worksheet2.update_cell(zikangime, 4, discussionstart)################################################書き込み
    worksheet2.update_cell(zikangime, 5, discussionfinish)################################################書き込み
    worksheet2.update_cell(zikangime, 3, "ari")################################################書き込み



    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペーす
    client = WebClient(token)
    #評価する相手のuserID取ってくる
    chan_id = "C025ET1R3UG"###chatお知らせチャンネル

    # DMを送信する
    client.chat_postMessage(channel=chan_id, text= "議論部屋"  + zikangime + "に" + discussionstart + "から" + discussionfinish +"までのDERCが設定されました。" + "参加される方は開始時刻までに賭けを行ってください。")
    #評価を通知するプログラム終わり



    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペーす
    client = WebClient(token)
    #評価する相手のuserID取ってくる
    chan_id = chan_IDlist[Number]###chatお知らせチャンネル

    # DMを送信する
    client.chat_postMessage(channel=chan_id, text= "この議論部屋に" + discussionstart + "から" + discussionfinish +"までのDERCが設定されました。" + "参加される方は開始時刻までに賭けを行ってください。")
    #評価を通知するプログラム終わり



    return redirect('/Thankyou_Chat')

#賭け対象選択ページ
@app.route('/kake_chat', methods=['GET'])
def kake_chat():
    channel = session['channel']
    name = session['name']
    all_worksheet2 = np.array(worksheet2.get_all_values())#worksheet2の全てのログを持ってくる。################################################

    chan_list = all_worksheet2[:, 1]#シート2のチャンネルリストをとってくる。
    chanNumber = 1
    for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
        if i != channel:
            chanNumber += 1
        elif i == channel:
            break
    session['chanNumber'] = chanNumber

    starttimestr = all_worksheet2[chanNumber - 1][3]
    finishtimestr= all_worksheet2[chanNumber - 1][4]
    all_worksheet1 = np.array(worksheet1.get_all_values())#worksheet1の全てのログを持ってくる。################################################
    ozzu_list = all_worksheet1[:, 3] #ozzu_listからユーザーのオッズを一次元配列で取得。

    

    kakezyouhou = []

    for i in range(len(all_user)):
        kakezyouhou.append([all_user[i], ozzu_list[i + 2]])#上記の4つの一次元配列を足し合わせて二次元配列にする。

    zibun = all_user.index(name)#賭け対象選択ページで自分の名前を表示させないために配列の何番目が自分なのか取得。
    kakezyouhou.pop(zibun)
 
    point =  int(all_worksheet1[zibun + 2][4])#自分のポイント数を取得
    kakepointlow = point//10#賭けることができる最低ポイント数を取得
    kakepointhigh = kakepointlow*2#賭けることができる最高ポイント数を取得

    kakerange = []
    for p in range(kakepointlow,kakepointhigh + 1):#最低ポイント～最高ポイントで１ずつ配列に入れる。
        kakerange.append(p)
   
    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
        
    return render_template('kake_chat.html',
    title='Setting',
    arinasi = "は議論が設定されていますが変更しますか？",
    start = starttimestr,
    finish = finishtimestr,
    channel=channel,
    kakezyouhou = kakezyouhou,
    point = point,
    kakepointlow = kakepointlow,
    kakepointhigh = kakepointhigh,
    kakerange = kakerange,
    name = name,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    kakesuu = kakepointhigh -kakepointlow + 1#賭けポイントの数
    )

@app.route('/kake_chat', methods=['POST'])
def kake_chat_POST():
    
    name = session['name']
    chanNumber = session['chanNumber']
    session.pop('chanNumber', None)
    channel = session['channel']
    session.pop(chanNumber,chanNumber)
    print(chanNumber)
    

    #賭け情報の書き込み
    kakeperson = request.form.get('kakeperson')#賭ける対象
    kakepoint = request.form.get('kakepoint')#賭けるポイント数
    zibun = all_user.index(name)#自分の名前の番号取得
    worksheet2.update_cell(chanNumber, (2 * zibun) + 6, kakeperson)#自分が賭けた人を記録###########################################################書き込み
    worksheet2.update_cell(chanNumber, (2 * zibun) + 7, kakepoint)#自分が賭けたポイント数を記録###########################################################書き込み

    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペース
    client = WebClient(token)
    #自分のuserID取ってくる
    user_id = all_user_ID[zibun]#評価相手のslackのIDを取ってくる。
    # DMを開き，channelidを取得する．
    res = client.conversations_open(users=user_id)
    dm_id = res['channel']['id']

    # DMを送信する
    client.chat_postMessage(channel=dm_id, text= "chat議論であなたは" + channel + "のお題で" + kakeperson + "に" + kakepoint + "ポイントの賭けを行いました。")
    #評価を通知するプログラム終わり


    return redirect('/Thankyou_Chat')

#Thank you言うページ
@app.route('/Thankyou_Chat', methods=['GET'])
def Thankyou_Chat():
    name = session['name']
    print(name)
    channel = session['channel'] 
    session.pop(channel,channel)
    all_worksheet2 = np.array(worksheet2.get_all_values())#worksheet2の全てのログを持ってくる。################################################
    chan_list = all_worksheet2[:, 1]#チャンネルリストを取得
    Number = 1
    for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
        if i != channel:
            Number += 1
        elif i == channel:
            break
    print(Number)
    starttimestr = all_worksheet2[Number - 1][3]#議論の始まりの時間取得
    finishtimestr= all_worksheet2[Number - 1][4]#議論の終わりの時間取得
    zibun = all_user.index(name)#自分の名前の番号取得
    kakeperson = all_worksheet2[Number - 1][(2 * zibun) + 5]#自分が賭けた人を記録
    kakepoint = all_worksheet2[Number - 1][(2 * zibun) + 6]#自分が賭けたポイント数を記録
    
    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    return render_template('Thankyou_Chat.html',
    channel = channel,
    name = name,
    starttime =starttimestr,
    finishtime = finishtimestr,
    kakeperson = kakeperson,
    kakepoint = kakepoint,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    title='Thank you for your cooperation!!')

#評価ページ
@app.route('/Discussing_Chat', methods=['GET'])
def Discussing_Chat():
    channel = session['playingchannel']
    # slackのログを保存したスプレッドシートを指名する
    #SlackのチャンネルIDとチャンネル名を合わせる。
    worksheet_slacklog = workbook_slacklog_EventAPI.worksheet(channel)#チャンネルのログを取ってくる。
    all_worksheet_slacklog = np.array(worksheet_slacklog.get_all_values())#worksheet_slacklogの全てのログを持ってくる。###############################################
    all_worksheet2 = np.array(worksheet2.get_all_values())#worksheet2の全てのログを持ってくる。###############################################
  
    slacklog_time =  all_worksheet_slacklog[:, 1] # slacklog_timeにシート1からB（議論のログ）の列を一次元配列で取得。
    slacklogname_list = all_worksheet_slacklog[:, 2] #slacklogname_listにシート1からC（名前）の列を一次元配列で取得。
    slacklog_list = all_worksheet_slacklog[:, 3]  # slacklog_listにシート1からD（時間）の列を一次元配列で取得。
    hihyoukanum = all_worksheet_slacklog[:, 5]  # slacklog_listにシート1からF（批評家回数）の列を一次元配列で取得。]

    chan_list = all_worksheet2[:, 1]#チャンネルリストを取得
    Number = 1
    for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
        if i != channel:
            Number += 1
        elif i == channel:
            break
    finishtime = all_worksheet2[Number - 1][4]  # 終了時刻を格納

    slacklog = []
    name = session['name']
    
    for j in range(len(slacklogname_list)-2):
        if slacklogname_list[j + 2] != name:
             hihyoukanum[j + 2] = "tanin"
    

    for i in range(len(slacklogname_list)-2):
        if  slacklog_list[i + 2] != "": #ログがなくなったら終わり。     
            slacklog.append([slacklog_time[i+2], slacklog_list[i+2],slacklogname_list[i+2] , i, hihyoukanum[i+2]])#上記の4つの一次元配列を足し合わせて二次元配列にする。
    
        else:
            break
    
    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
    
    return render_template('Discussing_Chat.html', #上の一文でエラーが出たらログ、名前、日時のどこかが抜けている。
    data=slacklog,
    name = name,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    finishtime = finishtime,
    channel = channel,
    title=channel +"  " 'Log')

@app.route('/Discussing_Chat', methods=['POST'])
def Discussing_Chat_POST():
    log = request.form.get('item')
    print(log)
    return redirect('/')

#評価ページ（最初の評価以外はこのページを使用する。）
@app.route('/hyouka/<number>', methods=['GET'])
def hyouka(number):
#スプレッドシートに保存する用プログラム始まり
    name = session['name']#評価の欄に書き込む自分の名前を取ってくる。
    channel = session['playingchannel']
    # slackのログを保存したスプレッドシートを指名す
    # SlackのチャンネルIDとチャンネル名を合わせる。
    worksheet_slacklog1 = workbook_slacklog_EventAPI.worksheet(channel)################################################
    # 評価ボタンを押した部分の発言の場所をスプレッドシートから探す。
    #cell = worksheet_slacklog1.find(log)
    #評価欄に自分以外の名前があったらそれ以降のセルに記入する。
    useridcell = all_user.index(name)
    worksheet_slacklog1.update_cell(int(number) + 3, useridcell +7 , "good")################################################書き込み
#スプレッドシートに保存する用プログラム終わり

#評価を通知するプログラム始まり
    token = "設定してください"# ワークスペーす
    client = WebClient(token)
    #評価する相手のuserID取ってくる
    all_worksheet_slacklog1 = np.array(worksheet_slacklog1.get_all_values())#worksheet_slacklog1の全てのログを持ってくる。################################################
    user_id = all_worksheet_slacklog1[int(number) + 2, 0]
    post_content = all_worksheet_slacklog1[int(number) + 2, 1]

    # DMを開き，channelidを取得する．
    res = client.conversations_open(users=user_id)
    dm_id = res['channel']['id']

    # DMを送信する
    client.chat_postMessage(channel=dm_id, text= "チャット議論のチャンネル[" + channel +"]であなたの「" + post_content[0:10] + "」の投稿が評価されました。")
#評価を通知するプログラム終わり

#評価を自分に通知するプログラム始まり
    token = "設定してください"# ワークスペーす
    client = WebClient(token)
    #自分のuserID取ってくる

    zibun = all_user.index(name)#自分の名前の番号取得
    user_id = all_user_ID[zibun]#評価相手のslackのIDを取ってくる。

    # DMを開き，channelidを取得する．
    res = client.conversations_open(users=user_id)
    dm_id = res['channel']['id']

    # DMを送信する
    client.chat_postMessage(channel=dm_id, text= "chat議論で評価しました！")
#評価を通知するプログラム終わり

    return redirect('/Discussing_Chat')


#継続中に議論の時間を変更するページ。
@app.route('/Discussing_chat_change/<channel>', methods=['GET'])
def Discussing_chat_change(channel):
    name = session['name']
    all_worksheet2 = np.array(worksheet2.get_all_values())#worksheet2の全てのログを持ってくる。################################################
    chan_list = all_worksheet2[:, 1]#シート2のチャンネルリスト全体をとってくる。
    
    chanNum = 0
    for aaa in chan_list:#チャンネルが配列の中の何番目なのかを検索する。
        if aaa != channel:
            chanNum = chanNum + 1
        else:
            break  
    finish = all_worksheet2[chanNum , 4]#終了時刻の取得
    session['chanNum'] = chanNum#GETとPOSTの間だけ保持

    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    return render_template('Discussing_change.html',
    channel = channel,
    finish = finish,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    name = name,
    title='Ending time')

@app.route('/Discussing_chat_change/<channel>', methods=['POST'])
def Discussing_chat_change_POST(channel):
    discussionfinishdate = request.form.get('discussionfinishdate')#終了
    discussionfinishtime = request.form.get('discussionfinishtime')

    chanNum = session['chanNum']#GETとPOSTの間だけ保持
    session.pop('chanNum',None)

    discussionfinish = discussionfinishdate +" " +discussionfinishtime
    worksheet2.update_cell(chanNum + 1, 5, discussionfinish)################################################

    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペーす
    client = WebClient(token)
    #評価するチャンネルのID取ってくる
    chan_id ="C025ET1R3UG"##chat議論おしらせチャンネル

    # DMを送信する
    client.chat_postMessage(channel= chan_id, text= channel + "の終了時刻が" +  discussionfinish + "に変更されました。")
    #評価を通知するプログラム終わり

    return redirect('/Discussing_Chat')


#####################################################################################################chat議論のページ終わり#####################################################################################################

#####################################################################################################web議論のページ始まり#####################################################################################################

#ビデオ議論選択ページ
@app.route('/Channelselection_web', methods=['GET'])
def Channelselection_web():

    name = session['name']
    nam = session['login']
    all_webchan = np.array(webchan.get_all_values())#webchanの全てのログを持ってくる。################################################
    chan_list = all_webchan[:, 1]#シート2のチャンネルリストをとってくる。
    chan_info = all_webchan[:, 3]#チャンネルの議論の情報を取ってくる。
    chan_info_a = []#上のari,nasi,playingをDERC設定あり、DERC設定なし、DERCでの議論進行中、に変える。
    for i in range(len(chan_list)):
        if chan_info[i] == "ari":
            chan_info_a.append("ゲーム設定あり")

        elif chan_info[i] == "nasi":
            chan_info_a.append("ゲーム設定なし")

        elif chan_info[i] == "playing":
            chan_info_a.append("ゲーム進行中")

        elif chan_info[i] == "shuuryou":
            chan_info_a.append("この議論は終了しています。")

        elif chan_info[i] == "":
            chan_info_a.append("空白")

        else:
            chan_info_a.append("エラー")


    chan_a = []#チャンネル名とチャンネル情報を合わせた二次元配列
    for j in range(len(chan_info_a)):
        if chan_info_a[j] == "空白":
            break

        else:
            chan_a.append([chan_list[j], chan_info_a[j]])

    id = session['id']
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
    return render_template('Channelselection_web.html',
            name = name,
            zentai = Badgeinfo[0],
            discuss = Badgeinfo[1],
            discussLv1 = Badgeinfo[2],
            discussLv2 = Badgeinfo[3],
            hosuu = Badgeinfo[4],
            hosuuLv1 = Badgeinfo[5],
            hosuuLv2 = Badgeinfo[6],
            ritakoui = Badgeinfo[7],
            ritakouiLv1 = Badgeinfo[8],
            ritakouiLv2 = Badgeinfo[9],
            title='Channel selection(オンライン議論)',
            chan_list = chan_a)

#議論を選択したら、各議論の状態のページに行くことができる（議論中→評価ページ、議論前→賭けページ、など）
@app.route('/Discussing_Web/<channel>', methods=['GET'])
def Discussing_Web(channel):
    nam = session['login']
    Number = 0
    
    all_webchan = np.array(webchan.get_all_values())#webchanの全てのログを持ってくる。################################################
    chan_list = all_webchan[:, 1]# シート2のチャンネルリストをとってくる。
    # 注意！！クエリパラメーターのchannelをそのまま持ってくると、channelには実は"BBQ日程決め"などの本当に得たいものと"site.webmanifest"というものも入ることがわかったので、"site.webmanifest"を除外している。
    if channel != "site.webmanifest":
        chan = channel
        for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
            if i != chan:
                Number += 1
            elif i == chan:
                break
        session['Number'] = Number

    chan_list_PorA = all_webchan[:, 3] # シート2からチャンネルがDERC設定が有か無しかを取得（playing or not）。


    if chan_list_PorA[Number] == "ari":
        session['channel'] = channel
        return redirect('/kake_web')  #kake_webへ

    elif chan_list_PorA[Number] == "playing":
        session['channel'] = channel
        discussNo = all_webchan[Number, 2]#議論番号取ってくる。
        session['discussNo'] = discussNo
        return redirect('/webdiscuss')

    elif chan_list_PorA[Number] == "shuuryou":
        session['channel'] = channel
        print("ここまで")
        return redirect('/finish')

#議論情報「nasi」から飛んできた場合
@app.route('/ChannelSetting_Web', methods=['GET'])
def ChannelSetting_Web():
    nam = session['login']
    name = session['name']
    # 注意！！クエリパラメーターのchannelをそのまま持ってくると、channelには実は"BBQ日程決め"などの本当に得たいものと"site.webmanifest"というものも入ることがわかったので、"site.webmanifest"を除外している。
    
    id = session['id']
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
    return render_template('ChannelSetting_Web.html',#notなので賭けるページへ
        title='Setting',
        zentai = Badgeinfo[0],
        discuss = Badgeinfo[1],
        discussLv1 = Badgeinfo[2],
        discussLv2 = Badgeinfo[3],
        hosuu = Badgeinfo[4],
        hosuuLv1 = Badgeinfo[5],
        hosuuLv2 = Badgeinfo[6],
        ritakoui = Badgeinfo[7],
        ritakouiLv1 = Badgeinfo[8],
        ritakouiLv2 = Badgeinfo[9],
        name = name)

#ビデオ議論が設定できる。
@app.route('/ChannelSetting_Web', methods=['POST'])
def ChannelSetting_WebPOST():
    discussionstartdate = request.form.get('discussionstartdate')#開始
    discussionstarttime = request.form.get('discussionstarttime')
    discussionfinishdate = request.form.get('discussionfinishdate')#終了
    discussionfinishtime = request.form.get('discussionfinishtime')
    odai = request.form.get('odai')#お題を取ってくる。
    chan_list = webchan.col_values(2)  # シート2のチャンネルリストをとってくる。################################################
    webchan.update_cell(len(chan_list) + 1, 2, odai)################################################
    discussionstart = discussionstartdate +" " +discussionstarttime
    discussionfinish = discussionfinishdate +" " +discussionfinishtime
    webchan.update_cell(len(chan_list) + 1, 5, discussionstart)################################################
    webchan.update_cell(len(chan_list) + 1, 6, discussionfinish)################################################
    webchan.update_cell(len(chan_list) + 1, 4, "ari")################################################

    session['channel'] = odai

    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペーす
    client = WebClient(token)
    #評価するチャンネルのID取ってくる
    chan_id ="C022UPX11FB"##オンライン議論おしらせチャンネル

    # DMを送信する
    client.chat_postMessage(channel= chan_id, text= "「" + odai + "」というお題で" + discussionstart + "から" + discussionfinish +"までのDERCが設定されました。" + "参加される方は開始時刻までに賭けを行ってください。")
    #評価を通知するプログラム終わり



    return redirect('/Thankyou_web')



#賭け対象選択ページ
@app.route('/kake_web', methods=['GET'])
def kake_web():
    channel = session['channel']
    name = session['name']

    all_webchan = np.array(webchan.get_all_values())#webchanの全てのログを持ってくる。################################################
    all_worksheet1 = np.array(worksheet1.get_all_values())#webinfoの全てのログを持ってくる。################################################
    chan_list =all_webchan[:, 1]#チャンネルリストを取得
    Number = 1
    for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
        if i != channel:
            Number += 1
        elif i == channel:
            break

    starttimestr = all_webchan[Number - 1, 4]
    ozzu_list = all_worksheet1[:, 3] #ozzu_listからユーザーのオッズを一次元配列で取得。##
  

    kakezyouhou = []

    for i in range(len(all_user)):
        kakezyouhou.append([all_user[i], ozzu_list[i + 2]])#上記の4つの一次元配列を足し合わせて二次元配列にする。

    zibun = all_user.index(name)#賭け対象選択ページで自分の名前を表示させないために配列の何番目が自分なのか取得。
    kakezyouhou.pop(zibun)

    point =  int(all_worksheet1[zibun + 2, 4])#自分のポイント数を取得##
    kakepointlow = point//10#賭けることができる最低ポイント数を取得
    kakepointhigh = kakepointlow*2#賭けることができる最高ポイント数を取得

    kakerange = []
    for p in range(kakepointlow,kakepointhigh + 1):#最低ポイント～最高ポイントで１ずつ配列に入れる。
        kakerange.append(p)

    id = session['id']
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。    

    return render_template('kake_web.html',
    title='Setting',
    arinasi = "は議論が設定されていますが変更しますか？",
    start = starttimestr,
    channel=channel,
    kakezyouhou = kakezyouhou,
    point = point,
    kakepointlow = kakepointlow,
    kakepointhigh = kakepointhigh,
    kakerange = kakerange,
    name = name,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    kakesuu = kakepointhigh -kakepointlow + 1#賭けポイントの数
    )

#賭け対象選択後ページ
@app.route('/kake_web', methods=['POST'])
def kake_web_POST():
    
    name = session['name']
    channel = session['channel']
    chan_list =webchan.col_values(2)#チャンネルリストを取得################################################
    Number = 0
    for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
        if i != channel:
            Number += 1
        elif i == channel:
            break
    

    #賭け情報の書き込み
    kakeperson = request.form.get('kakeperson')#賭ける対象
    kakepoint = request.form.get('kakepoint')#賭けるポイント数
    zibun = all_user.index(name)#自分の名前の番号取得
    webchan.update_cell(Number + 1, (2 * zibun) + 7, kakeperson)#自分が賭けた人を記録################################################
    webchan.update_cell(Number + 1, (2 * zibun) + 8, kakepoint)#自分が賭けたポイント数を記録################################################

    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペース
    client = WebClient(token)
    #自分のuserID取ってくる
    user_id = all_user_ID[zibun]#評価相手のslackのIDを取ってくる。
    # DMを開き，channelidを取得する．
    res = client.conversations_open(users=user_id)
    dm_id = res['channel']['id']

    # DMを送信する
    client.chat_postMessage(channel=dm_id, text= "オンライン議論であなたは" + channel + "のお題で" + kakeperson + "に" + kakepoint + "ポイントの賭けを行いました。")
    #評価を通知するプログラム終わり

    return redirect('/Thankyou_web')

#Thank youと言うページ
@app.route('/Thankyou_web', methods=['GET'])
def Thankyou_web():
    name = session['name']
    channel = session['channel'] 
    session.pop(channel,channel)
    ############################
    all_webchan = np.array(webchan.get_all_values())#webchanの全てのログを持ってくる。################################################
    chan_list =all_webchan[:, 1]#チャンネルリストを取得
    Number = 0
    for i in chan_list:#チャンネルが何行目にあるか確認して行数をNumberに代入
        if i != channel:
            Number += 1
        elif i == channel:
            break
    starttimestr = all_webchan[Number, 4]#議論の始まりの時間取得##
    print(Number)
    print(chan_list)
    zibun = all_user.index(name)#自分の名前の番号取得
    kakeperson = all_webchan[Number , (2 * zibun) + 6]#自分が賭けた人を記録##
    kakepoint = all_webchan[Number, (2 * zibun) + 7]#自分が賭けたポイント数を記録##
    if kakepoint != " ":#賭けがあれば「1」無ければ「0」
        kakezyouhou = 0

    else:
        kakezyouhou = 1

    id = session['id']
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    return render_template('Thankyou_web.html',
    channel = channel,
    name = name,
    starttime =starttimestr,
    kakeperson = kakeperson,
    kakepoint = kakepoint,
    kakezyoukyou = kakezyouhou,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    title='Thank you for your cooperation!!')


#終了した議論に自分が関わっていたら成績が見れる。関わっていなかったらあなたはこの議論に参加していません。的なページを出す。
@app.route('/finish', methods=['GET'])
def Finish():
    channel = session['channel']
    name = session['name']
    all_webchan = np.array(webchan.get_all_values())#webchanの全てのログを持ってくる。################################################
    chan_list = all_webchan[:, 1]#シート2のチャンネルリスト全体をとってくる。
    chan_info_giron = all_webchan[:, 2]#チャンネルの議論の情報全体を取ってくる(議論1,議論2....など)
    chan_info = all_webchan[:, 3]#チャンネルの議論の情報全体を取ってくる（ari,playing,shuuryou）
    
    chanNum = 0
    for aaa in chan_list:#チャンネルが配列の中の何番目なのかを検索する。
        if aaa != channel:
            chanNum = chanNum + 1
        else:
            break

    chan_info_giron_Num = chan_info_giron[chanNum]#議論番号を取得(議論1,議論2....など)
    chan_info_Num = chan_info[chanNum]#議論情報を取得（ari,playing,shuuryou）

    id = session['id']
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
   
    if chan_info_Num == "shuuryou":  
        webDisinfo = workbook_webdiscuss.worksheet(chan_info_giron_Num)
        all_webDisinfo = np.array(webDisinfo.get_all_values())#webDisinfoの全てのログを持ってくる。################################################

        result = all_webDisinfo[43]#議論？の中の44行目「レベル１とレベル２の合計」の中で自分の欄が0以外だった場合、議論に参加していたという事。
        mNumber = all_user.index(name)#自分の番号何番目
        zibun_result = result[mNumber + 3]

        if zibun_result == 0:
            return render_template('finish.html',
            name = name,
            zentai = Badgeinfo[0],
            discuss = Badgeinfo[1],
            discussLv1 = Badgeinfo[2],
            discussLv2 = Badgeinfo[3],
            hosuu = Badgeinfo[4],
            hosuuLv1 = Badgeinfo[5],
            hosuuLv2 = Badgeinfo[6],
            ritakoui = Badgeinfo[7],
            ritakouiLv1 = Badgeinfo[8],
            ritakouiLv2 = Badgeinfo[9],
            title='Result')

        else:
            kakeaite = all_webDisinfo[32][mNumber + 3]#賭けた相手
            kakepoint = all_webDisinfo[33][mNumber + 3] #賭けたポイント
            hihyoukapoint1 = all_webDisinfo[38][mNumber + 3]#レベル１で得たポイント
            seikousippai = all_webDisinfo[40][mNumber + 3]#成功/失敗
            hihyoukapoint2 = all_webDisinfo[41][mNumber + 3]#レベル２で得たポイント
            sougoupoint = all_webDisinfo[43][mNumber + 3]#総合的にポイントの加算・減算
            
            return render_template('finish.html',
            name = name,
            channel = channel,
            kakeaite = kakeaite,
            kakepoint = kakepoint,
            hihyoukapoint1 = hihyoukapoint1,
            seikousippai = seikousippai,
            hihyoukapoint2 = hihyoukapoint2,
            sougoupoint = sougoupoint,
            zentai = Badgeinfo[0],
            discuss = Badgeinfo[1],
            discussLv1 = Badgeinfo[2],
            discussLv2 = Badgeinfo[3],
            hosuu = Badgeinfo[4],
            hosuuLv1 = Badgeinfo[5],
            hosuuLv2 = Badgeinfo[6],
            ritakoui = Badgeinfo[7],
            ritakouiLv1 = Badgeinfo[8],
            ritakouiLv2 = Badgeinfo[9],
            title='Result')

    else:
        return render_template('finish.html',
        zentai = Badgeinfo[0],
        discuss = Badgeinfo[1],
        discussLv1 = Badgeinfo[2],
        discussLv2 = Badgeinfo[3],
        hosuu = Badgeinfo[4],
        hosuuLv1 = Badgeinfo[5],
        hosuuLv2 = Badgeinfo[6],
        ritakoui = Badgeinfo[7],
        ritakouiLv1 = Badgeinfo[8],
        ritakouiLv2 = Badgeinfo[9],
        name = name,
        title='Result')


##web議論を行うページ（評価した後もこのページをリダイレクトしている。）
##やっていること：DBから自分の行を取り出して被評価の時間を出している。
##そして、評価されていたら（actionが1になっていたら）、HTMLに評価されたよという表示を出し、actionfinishtimeを0に戻す。）
@app.route('/webdiscuss', methods=['GET'])
def webdiscuss():
    channel = session['channel']
    discussNo = session['discussNo']
    nam = session['login']
    Number = 0
    name = session['name']
    hyoukalist = []
    db = get_db()
    id_DB = all_user.index(name) +1
    print(id_DB)
    print(discussNo)
    cur_me = db.execute("select * from {discussNo} where id = {id_DB}".format(id_DB = id_DB, discussNo = discussNo))##DBの中の自分の情報を取得しておく
    hyoukalist = cur_me.fetchall()
    cur_test = db.execute("select * from {discussNo} where id = 11 ".format(discussNo = discussNo))##DBの中の(test)の情報を取得（議論の情報を取得）しておく
    discuss_info = cur_test.fetchall()
    ###以下、参加している人と、自分以外票がボタンを表示しないようにする。###
    userlist = []
    for par in range(1,11):
        cur_par = db.execute("select * from {discussNo} where id = {par}".format(par = par, discussNo = discussNo))##DBの中の各被験者の情報を取得
        user_DB = cur_par.fetchall()
        if user_DB[0][3] == "1":
            userlist.append(user_DB[0][0])
            user_DB.clear()
    if hyoukalist[0][0] in userlist:
        userlist.remove(hyoukalist[0][0])###最後に自分の名前を削除する。
    ###参加している人と、自分以外票がボタンを表示しないようにする。終わり###
    close_db()##コードがくちゃくちゃ過ぎるが一度、データベースの接続を終了（これがないとエラーになるため。）

    #配列中のNoneを全て消す。
    hyoukalist_filtered = []
    for ppp in range(48):
        if hyoukalist[0][ppp] is not None:
            hyoukalist_filtered.append(hyoukalist[0][ppp])
        else:
            pass

    #最初の二つ（nameとidを消す）
    hyoukalist_filtered.pop(0)
    hyoukalist_filtered.pop(0)
    action = hyoukalist_filtered[0]##自分が評価されたかどうかを格納
    hyoukalist_filtered.pop(0)#actionfinishtimeを消す。
    hyoukalist_filtered.pop(0)#participantを消す。

    ##もしactionfinishtimeが1だったら（自分が評価されていたら）0に変える。
    if action == "1":
        # model class（DB書き込み用）
        class actionDB(Base):
          __tablename__ = discussNo
          __table_args__ = {'extend_existing': True}
          id = Column(Integer, primary_key=True)
          actionfinishtime = Column(String(255))

         # get Dict data
        def toDict(self):

            return {
                'id':int(self.id), 
                'actionfinishtime':str(self.actionfinishtime)
            }
         
        Session = sessionmaker(bind = engine)
        ses = Session()
        mydata = ses.query(actionDB).filter(actionDB.id == id_DB).one()
        mydata.actionfinishtime = 0
        ses.add(mydata)
        ses.commit()
        ses.close()

    ##もしtestのparticipantが1だったら（参加者リストが更新されていなかったら）参加者リストを更新して0に変える。
    if discuss_info[0][3] == "1":
        webinfo = workbook_webdiscuss.worksheet(discussNo)################################################
        all_webinfo = np.array(webinfo.get_all_values())#webchanの全てのログを持ってくる。################################################
        # model class（DB書き込み用）
        class participantDB(Base):
          __tablename__ = discussNo
          id = Column(Integer, primary_key=True)
          participant = Column(String(255))

        # get Dict data
        def toDict(self):
            return {
                'id':int(self.id), 
                'participant':str(self.participant)
            }
        Session = sessionmaker(bind = engine)
        ses = Session() 

        for ll in range(1,11):
            if all_webinfo[32][2 + ll] in all_user:#
                mydata = ses.query(participantDB).filter(participantDB.id == ll).one()
                mydata.participant = 1
                ses.add(mydata)

        mydata = ses.query(participantDB).filter(participantDB.id == 11).one()
        mydata.participant = 0
        ses.add(mydata)
        
        ses.commit()
        ses.close()

    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
        
    return render_template('Discussing_Web.html', 
    channel = channel,
    userlist = userlist, 
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    hyoukalist = hyoukalist_filtered,
    action = action,

    name = name,)  # 議論が始まっているのでDiscussing_Web.htmlを表示。

#web評価の作業（評価を実行後/webdiscussをredirectする。）
@app.route('/Discussing_Web2/<hyouka>', methods=['GET'])
def Discussing_Web2(hyouka):
#スプレッドシートに保存する用プログラム始まり
    name = session['name']#評価の欄に書き込む自分の名前を取ってくる。
    channel = session['channel']
    # チャンネルIDとチャンネル名を合わせる。
    discussNo = session['discussNo'] 
    webinfo = workbook_webdiscuss.worksheet(discussNo)################################################
    all_webinfo = np.array(webinfo.get_all_values())#webchanの全てのログを持ってくる。################################################
    discususer_list = all_user

    #評価した相手の行の処理(uNumber=評価相手の番号、mNumber=自分の番号)
    uNumber  = discususer_list.index(hyouka)#評価する相手の名前を見つけてくる。
    hihyoukacount =  all_webinfo[uNumber, 2]#評価される相手の批評価回数##
    
    ###以下、スプレッドシートへの書き込み###
    webinfo.update_cell(uNumber +1, (int(hihyoukacount)*2) + 8, name)#自分の名前を書き込む################################################書き込み
    now = datetime.datetime.now()
    webinfo.update_cell(uNumber+1, (int(hihyoukacount)*2) + 7, (str(now.hour) +':'+  str(now.minute)))#評価した時間を書き込むjson.dumps(now.hour, default=support_datetime_default)################################################書き込み
    ###スプレッドシートへの書き込み終わり###

    ###以下、DBへの書き込み###
    # model class
    class hyoukaDB(Base):
      __tablename__ = discussNo
      __table_args__ = {'extend_existing': True}
      id = Column(Integer, primary_key=True)
      actionfinishtime = Column(String(255))
      for oo in range(1,48):#hihyouka?にColumn(String(255))を入れまくる。
        exec_command = 'hihyouka' + str(oo) + '= Column(String(255))'
        exec(exec_command)


    # get Dict data
    def toDict(self):
        return {
            'id':int(self.id), 
            'actionfinishtime':str(self.actionfinishtime),
            'hihyouka1':str(self.actionfinishtime),
            'hihyouka2':str(self.actionfinishtime),
            'hihyouka3':str(self.actionfinishtime),
            'hihyouka4':str(self.actionfinishtime),
            'hihyouka5':str(self.actionfinishtime),
            'hihyouka6':str(self.actionfinishtime),
            'hihyouka7':str(self.actionfinishtime),
            'hihyouka8':str(self.actionfinishtime),
            'hihyouka9':str(self.actionfinishtime),
            'hihyouka10':str(self.actionfinishtime),
            'hihyouka11':str(self.actionfinishtime),
            'hihyouka12':str(self.actionfinishtime),
            'hihyouka13':str(self.actionfinishtime),
            'hihyouka14':str(self.actionfinishtime),
            'hihyouka15':str(self.actionfinishtime),
            'hihyouka16':str(self.actionfinishtime),
            'hihyouka17':str(self.actionfinishtime),
            'hihyouka18':str(self.actionfinishtime),
            'hihyouka19':str(self.actionfinishtime),
            'hihyouka20':str(self.actionfinishtime),
            'hihyouka21':str(self.actionfinishtime),
            'hihyouka22':str(self.actionfinishtime),
            'hihyouka23':str(self.actionfinishtime),
            'hihyouka24':str(self.actionfinishtime),
            'hihyouka25':str(self.actionfinishtime),
            'hihyouka26':str(self.actionfinishtime),
            'hihyouka27':str(self.actionfinishtime),
            'hihyouka28':str(self.actionfinishtime),
            'hihyouka29':str(self.actionfinishtime),
            'hihyouka30':str(self.actionfinishtime),
            'hihyouka31':str(self.actionfinishtime),
            'hihyouka32':str(self.actionfinishtime),
            'hihyouka33':str(self.actionfinishtime),
            'hihyouka34':str(self.actionfinishtime),
            'hihyouka35':str(self.actionfinishtime),
            'hihyouka36':str(self.actionfinishtime),
            'hihyouka37':str(self.actionfinishtime),
            'hihyouka38':str(self.actionfinishtime),
            'hihyouka39':str(self.actionfinishtime),
            'hihyouka40':str(self.actionfinishtime),
            'hihyouka41':str(self.actionfinishtime),
            'hihyouka42':str(self.actionfinishtime),
            'hihyouka43':str(self.actionfinishtime),
            'hihyouka44':str(self.actionfinishtime),
            'hihyouka45':str(self.actionfinishtime),
            'hihyouka46':str(self.actionfinishtime),
            'hihyouka47':str(self.actionfinishtime),
            'hihyouka48':str(self.actionfinishtime),
        }
    Session = sessionmaker(bind = engine)
    ses = Session()
    hyoukasubject = ses.query(hyoukaDB).filter(hyoukaDB.id == uNumber + 1).one()##評価する相手のidを入れる。
    print(uNumber)
    hyoukasubject.actionfinishtime = 1##actionの部分を1に変える。
    hihyoukacount_DB = int(hihyoukacount) + 1
    exec_code = 'hyoukasubject.hihyouka' + str(hihyoukacount_DB) + '='  + '"' + str(now.hour) + '時' + str(now.minute) + '分' +'"' ##相手の評価の部分に時間を記入する。
    exec(exec_code)
    hyoukasubject.actionfinishtime = "1"##actionを1にして評価されたという」記録を残す。
    ses.add(hyoukasubject)
    ses.commit()
    ses.close()

    ###DBの書き込み終わり###

    #評価された回数を数えてその時間を表示させるための処理
    print(discususer_list)
    mNumber = discususer_list.index(name)
    hihyoukanum =  all_webinfo[mNumber, 2]



    return redirect('/webdiscuss')

#継続中に議論の時間を変更するページ。
@app.route('/Discussing_web_change/<channel>', methods=['GET'])
def Discussing_web_change(channel):
    channel = session['channel']
    name = session['name']
    all_webchan = np.array(webchan.get_all_values())#webchanの全てのログを持ってくる。################################################
    chan_list = all_webchan[:, 1]#シート2のチャンネルリスト全体をとってくる。
    
    chanNum = 0
    for aaa in chan_list:#チャンネルが配列の中の何番目なのかを検索する。
        if aaa != channel:
            chanNum = chanNum + 1
        else:
            break  
    finish = all_webchan[chanNum , 5]#終了時刻の取得
    session['chanNum'] = chanNum#GETとPOSTの間だけ保持

    id = session['id']
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    return render_template('Discussing_change.html',
    channel = channel,
    finish = finish,
    name = name,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    title='Ending time')

@app.route('/Discussing_web_change/<channel>', methods=['POST'])
def Discussing_web_change_POST(channel):
    discussionfinishdate = request.form.get('discussionfinishdate')#終了
    discussionfinishtime = request.form.get('discussionfinishtime')

    chanNum = session['chanNum']#GETとPOSTの間だけ保持
    session.pop('chanNum',None)

    discussionfinish = discussionfinishdate +" " +discussionfinishtime
    webchan.update_cell(chanNum + 1, 6, discussionfinish)################################################

    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペーす
    client = WebClient(token)
    #評価するチャンネルのID取ってくる
    chan_id ="C022UPX11FB"##web議論おしらせチャンネル

    # DMを送信する
    client.chat_postMessage(channel= chan_id, text= channel + "の終了時刻が" +  discussionfinish + "に変更されました。")
    #評価を通知するプログラム終わり

    return redirect('/webdiscuss')
#####################################################################################################web議論のページ終わり#####################################################################################################



#####################################################################################################歩数関連のページ始まり#####################################################################################################
#ページ選択ができるページ
@app.route('/hosuu', methods=['GET'])
def hosuu():
    name = session['name']
    id = session['id']
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
    return render_template('hosuu.html',
    name = name,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    title='歩数計算')


#今までの歩数や、履歴を見れるページ
@app.route('/hosuurireki', methods=['GET'])
def hosuurireki():
    name = session['name']
    mNumber = all_user.index(name)#自分の番号何番目
    all_hosuukeisan = np.array(hosuukeisan.get_all_values())#hosuukeisanの全てのログを持ってくる。################################################

    date = all_hosuukeisan[:, 1]#日にちを取得
    hosuurireki = all_hosuukeisan[:, mNumber + 2]#自分の歩数の履歴を取得
    kakerireki = all_hosuukeisan[:, mNumber + 28]#自分の賭けの履歴を取

    hosuukekka = []
    hosuukekka.append(["日時", "自分の歩数", "賭けた相手" , "賭けたポイント" , "賭け成功/失敗"])#紹介文を先に入れておく

    for i in range(50):
      hosuukekka.append([date[i+7] , hosuurireki[i+7] , kakerireki[3 * i + 8] , kakerireki[3 * i + 9] , kakerireki[3 * i + 7]])#上記の4つの一次元配列を足し合わせて二次元配列にする。
    
    id = session['id']
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    return render_template('hosuurireki.html',
    name = name,
    hosuukekka = hosuukekka,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    title='歩数関連履歴')

#歩数の賭けが終わった後に表示されるページ
@app.route('/hosuukakefin', methods=['GET'])
def hosuukakefin():
    name = session['name']
    mNumber = all_user.index(name)#自分の番号何番目
    all_hosuukeisan = np.array(hosuukeisan.get_all_values())#hosuukeisanの全てのログを持ってくる。################################################

    kakeperson = all_hosuukeisan[ 4 , mNumber + 28]#賭けた対象を取得
    kakepoint = all_hosuukeisan[ 5 , mNumber + 28]#賭けたポイントを取得
    

    if kakeperson == " ":
        return redirect('/hosuukake')#賭けている人がいない場合、賭けページに戻る。
    
    else:
        id = session['id']
        Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
        return render_template('hosuukakefin.html',
        name = name,
        kakepoint = kakepoint,
        kakeperson = kakeperson,
        zentai = Badgeinfo[0],
        discuss = Badgeinfo[1],
        discussLv1 = Badgeinfo[2],
        discussLv2 = Badgeinfo[3],
        hosuu = Badgeinfo[4],
        hosuuLv1 = Badgeinfo[5],
        hosuuLv2 = Badgeinfo[6],
        ritakoui = Badgeinfo[7],
        ritakouiLv1 = Badgeinfo[8],
        ritakouiLv2 = Badgeinfo[9],
        title='Thank you')

#歩数の賭けができる
@app.route('/hosuukake', methods=['GET'])
def hosuukake():
    name = session['name']
    all_worksheet1 = np.array(worksheet1.get_all_values())#worksheet1の全てのログを持ってくる。################################################

    hosuuozzu = all_worksheet1[:, 5] #ユーザーの歩数でのオッズを一次元配列で取得。
    kakezyouhou = []

    for i in range(len(all_user)):
        kakezyouhou.append([all_user[i], hosuuozzu[i + 2]])#上記の4つの一次元配列を足し合わせて二次元配列にする。

    mNumber = all_user.index(name)#賭け対象選択ページで自分の名前を表示させないために配列の何番目が自分なのか取得。
    kakezyouhou.pop(mNumber)
 
    point =  int(all_worksheet1[mNumber+ 2][4])#自分のポイント数を取得
    kakepointlow = point//10#賭けることができる最低ポイント数を取得
    kakepointhigh = kakepointlow*2#賭けることができる最高ポイント数を取得

    kakerange = []
    for p in range(kakepointlow,kakepointhigh + 1):#最低ポイント～最高ポイントで１ずつ配列に入れる。
        kakerange.append(p)

    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    return render_template('hosuukake.html',
    title='歩数賭けページ',
    kakezyouhou = kakezyouhou,
    point = point,
    kakepointlow = kakepointlow,
    kakepointhigh = kakepointhigh,
    kakerange = kakerange,
    name = name,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    kakesuu = kakepointhigh -kakepointlow + 1#賭けポイントの数
    )

@app.route('/hosuukake', methods=['POST'])
def hosuukakePOST():
    name = session['name']
    mNumber = all_user.index(name)#賭け対象選択ページで自分の名前を表示させないために配列の何番目が自分なのか取得。
    kakeperson = request.form.get('kakeperson')#開始
    kakepoint = request.form.get('kakepoint')

    hosuukeisan.update_cell(5, mNumber + 29, kakeperson)################################################書き込み
    hosuukeisan.update_cell(6, mNumber + 29, kakepoint)################################################書き込み
    

    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペース
    client = WebClient(token)
    #自分のuserID取ってくる
    user_id = all_user_ID[mNumber]#自分のslackのIDを取ってくる。
    # DMを開き，channelidを取得する．
    res = client.conversations_open(users=user_id)
    dm_id = res['channel']['id']

    # DMを送信する
    client.chat_postMessage(channel=dm_id, text= "歩数計算であなたは" + kakeperson + "に" + kakepoint + "ポイントの賭けを行いました。")
    #評価を通知するプログラム終わり

    return redirect('/hosuukakefin')

#####################################################################################################歩数関連のページ終わり#####################################################################################################


#####################################################################################################利他行為のページ始まり#####################################################################################################
#ページ選択ができるページ
@app.route('/rita', methods=['GET'])
def rita():
    name = session['name']

    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
  
    return render_template('rita.html',
    name = name,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    title='利他行為')

#利他行為の履歴に入れる情報:自分が何回利他行為を行ったか、自分が利他行為を何回受け取ったか、誰に賭けたのか、賭けが成功したか。
@app.route('/ritarireki', methods=['GET'])
def ritarireki():
    name = session['name']
    mNumber = all_user.index(name)#自分の番号何番目
    all_ritasheet = np.array(ritasheet.get_all_values())#ritasheetの全てのログを持ってくる。################################################

    date = all_ritasheet[:, 10]#日にちを取得
    ritarireki = all_ritasheet[:, mNumber + 11]#自分の利他行為の履歴を取得

    rita = []
    rita.append(["日時", "利他行為されたと他者に認定された回数", "Lv1の受け取りポイント" , "利他行為されたと自らで認定した回数" , "賭けた人" , "賭けたポイント" , "Lv2の受け取りポイント"])#紹介文を先に入れておく

    for i in range(20):
      rita.append([date[i*7+9] , ritarireki[i*7+9] , ritarireki[i*7+10] , ritarireki[i*7+11] , ritarireki[i*7+13] , ritarireki[i*7+14] , ritarireki[i*7+15]])#上記の5つの一次元配列を足し合わせて二次元配列にする。
    
    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    return render_template('ritarireki.html',
    name = name,
    rita = rita,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    title='利他行為履歴')


#賭けが終わった後に表示されるページ
@app.route('/ritakakefin', methods=['GET'])
def ritakakefin():
    name = session['name']
    mNumber = all_user.index(name)#自分の番号何番目
    all_ritasheet = np.array(ritasheet.get_all_values())#ritasheetの全てのログを持ってくる。################################################

    kakeperson = all_ritasheet[ 5 , mNumber + 11]#賭けた対象を取得
    kakepoint = all_ritasheet[ 6 , mNumber + 11]#賭けたポイントを取得
    

    if kakeperson == " ":
      return redirect('/ritakake')#賭けている人がいない場合、賭けページに戻る。
    
    else :
        id = session['id']
        updateBadgeinfo(id)
        Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。
        return render_template('ritakakefin.html',
        name = name,
        kakepoint = kakepoint,
        kakeperson = kakeperson,
        zentai = Badgeinfo[0],
        discuss = Badgeinfo[1],
        discussLv1 = Badgeinfo[2],
        discussLv2 = Badgeinfo[3],
        hosuu = Badgeinfo[4],
        hosuuLv1 = Badgeinfo[5],
        hosuuLv2 = Badgeinfo[6],
        ritakoui = Badgeinfo[7],
        ritakouiLv1 = Badgeinfo[8],
        ritakouiLv2 = Badgeinfo[9],
        title='Thank you')

#賭けができる
@app.route('/ritakake', methods=['GET'])
def ritakake():
    name = session['name']
    all_worksheet1 = np.array(worksheet1.get_all_values())#worksheet1の全てのログを持ってくる。################################################

    ritaozzu = all_worksheet1[:, 6] #ユーザーの歩数でのオッズを一次元配列で取得。
    kakezyouhou = []

    for i in range(len(all_user)):
        kakezyouhou.append([all_user[i], ritaozzu[i + 2]])#上記の4つの一次元配列を足し合わせて二次元配列にする。

    mNumber = all_user.index(name)#賭け対象選択ページで自分の名前を表示させないために配列の何番目が自分なのか取得。
    kakezyouhou.pop(mNumber)
 
    point =  int(all_worksheet1[mNumber+ 2][4])#自分のポイント数を取得
    kakepointlow = point//10#賭けることができる最低ポイント数を取得
    kakepointhigh = kakepointlow*2#賭けることができる最高ポイント数を取得

    kakerange = []
    for p in range(kakepointlow,kakepointhigh + 1):#最低ポイント～最高ポイントで１ずつ配列に入れる。
        kakerange.append(p)

    id = session['id']
    updateBadgeinfo(id)
    Badgeinfo = getBadgeinfo(id)#バッヂの情報を取得する関数の呼び出し。

    return render_template('ritakake.html',
    title='利他行為賭けページ',
    kakezyouhou = kakezyouhou,
    point = point,
    kakepointlow = kakepointlow,
    kakepointhigh = kakepointhigh,
    kakerange = kakerange,
    name = name,
    zentai = Badgeinfo[0],
    discuss = Badgeinfo[1],
    discussLv1 = Badgeinfo[2],
    discussLv2 = Badgeinfo[3],
    hosuu = Badgeinfo[4],
    hosuuLv1 = Badgeinfo[5],
    hosuuLv2 = Badgeinfo[6],
    ritakoui = Badgeinfo[7],
    ritakouiLv1 = Badgeinfo[8],
    ritakouiLv2 = Badgeinfo[9],
    kakesuu = kakepointhigh -kakepointlow + 1#賭けポイントの数
    )

@app.route('/ritakake', methods=['POST'])
def ritakakePOST():
    name = session['name']
    mNumber = all_user.index(name)#賭け対象選択ページで自分の名前を表示させないために配列の何番目が自分なのか取得。
    kakeperson = request.form.get('kakeperson')#開始
    kakepoint = request.form.get('kakepoint')

    ritasheet.update_cell(6, mNumber + 12, kakeperson)################################################書き込み
    ritasheet.update_cell(7, mNumber + 12, kakepoint)################################################書き込み
    
    #評価を通知するプログラム始まり
    token = "設定してください"# ワークスペース
    client = WebClient(token)
    #自分のuserID取ってくる
    user_id = all_user_ID[mNumber]#自分のslackのIDを取ってくる。
    # DMを開き，channelidを取得する．
    res = client.conversations_open(users=user_id)
    dm_id = res['channel']['id']

    # DMを送信する
    client.chat_postMessage(channel=dm_id, text= "利他行為の賭けであなたは" + kakeperson + "に" + kakepoint + "ポイントの賭けを行いました。")
    #評価を通知するプログラム終わり

    return redirect('/ritakakefin')

#####################################################################################################利他行為のページ終わり#####################################################################################################

#ログアウトのため
# logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('name', None)
    session.pop('login',None)
    session.pop('id',None)
    return redirect('/Login')

#以下メモ
#GASからDBを操作したいと思ったときに、定期実行の方法がないため次の方法で行う。
#pythonファイルで、ssの情報とDBの情報が違っていれば（ssが更新されていれば）スプレッドシートの情報をDBに書き込む、という関数を1分ごとに起動させる
#一番行いたいこととしては、データの保存方法をスプレッドシートにせず、DBのみにしてスプレッドっシートの使用を完全にやめて、全てpythonファイルとDBのみにすることだが、時間がなく、しょうがないので以下の方法で行う。
#「DDG-database+チャットログ（重要）」のポイント管理（スプレッドシート）の3L~15Vを「derc.db」のbadgedataの3列目（receivePt_zentai）~12列目（receivePt_ritakouiLv2）の情報に更新する。
#定期実行を関数を呼ぶことによって行いたいが、関数にしてflask内でその関数を呼んで実行するというやり方だとなぜかできないため、一つのページを更新した時に関数を呼ぶようにし、実験中はサーバー側でwebページを開いておき、定期で更新することでスクリプトが1分ごとに走る仕組みにする。
def UpdateDB():
    all_infoDBss = np.array(worksheet1.get_all_values())#ポイント管理のシートの全ての情報をとってくる。##############################################
    
    # model class（badgedata用）
    class Badgedata(Base):
        __tablename__ = 'badgedata'
        __table_args__ = {'extend_existing': True}
    
        id = Column(Integer, primary_key=True)
        receivePt_zentai = Column(Integer)
        receivePt_discuss = Column(Integer)
        receivePt_discussLv1 = Column(Integer)
        receivePt_discussLv2 = Column(Integer)
        receivePt_hosuu = Column(Integer)
        receivePt_hosuuLv1 = Column(Integer)
        receivePt_hosuuLv2 = Column(Integer)
        receivePt_ritakoui = Column(Integer)
        receivePt_ritakouiLv1 = Column(Integer)
        receivePt_ritakouiLv2 = Column(Integer)

    # get Dict data
    def toDict(self):
        return {
            'id':int(self.id), 
            'receivePt_zentai' : int(self.receivePt_zentai),
            'receivePt_discuss' : int(self.receivePt_discuss),
            'receivePt_discussLv1' : int(self.receivePt_discussLv1),
            'receivePt_discussLv2' : int(self.receivePt_discussLv2),
            'receivePt_hosuu' : int(self.receivePt_hosuu),
            'receivePt_hosuuLv1' : int(self.receivePt_hosuuLv1),
            'receivePt_hosuuLv2' : int(self.receivePt_hosuuLv2),
            'receivePt_ritakoui' : int(self.receivePt_ritakoui),
            'receivePt_ritakouiLv1' : int(self.receivePt_ritakouiLv1),
            'receivePt_ritakouiLv2' : int(self.receivePt_ritakouiLv2),
        }

    for human in range(len(all_user)):
        id = human + 1#その人のidを取ってくる。
        ###ss（スプレッドシート）から情報を取ってくる。
        print(all_infoDBss[2 + human][12])
        print(human)
        receivePt_zentai_ss = int(all_infoDBss[2 + human][12])
        receivePt_discuss_ss = int(all_infoDBss[2 + human][13])
        receivePt_discussLv1_ss = int(all_infoDBss[2 + human][14])
        receivePt_discussLv2_ss = int(all_infoDBss[2 + human][15])
        receivePt_hosuu_ss = int(all_infoDBss[2 + human][16])
        receivePt_hosuuLv1_ss = int(all_infoDBss[2 + human][17])
        receivePt_hosuuLv2_ss = int(all_infoDBss[2 + human][18])
        receivePt_ritakoui_ss = int(all_infoDBss[2 + human][19])
        receivePt_ritakouiLv1_ss = int(all_infoDBss[2 + human][20])
        receivePt_ritakouiLv2_ss = int(all_infoDBss[2 + human][21])

        ###DBから情報を取ってくる。
        DBinfotwo = []
        DBinfo = []
        db = get_db()
        cur_DBss = db.execute("select * from badgedata where id = {id}".format(id = id))
        DBinfotwo = cur_DBss.fetchall()
        for kkk in range(30):#DBから取ってきたままだと2次元で扱いにくいため一次元に返還する。
            DBinfo.append(DBinfotwo[0][kkk])
            #以下それぞれの獲得ポイントを格納する。
        receivePt_zentai = DBinfo[2]
        receivePt_discuss = DBinfo[3]
        receivePt_discussLv1 = DBinfo[4]
        receivePt_discussLv2 = DBinfo[5]
        receivePt_hosuu = DBinfo[6]  
        receivePt_hosuuLv1 = DBinfo[7]
        receivePt_hosuuLv2 = DBinfo[8]
        receivePt_ritakoui = DBinfo[9]
        receivePt_ritakouiLv1 = DBinfo[10]
        receivePt_ritakouiLv2 = DBinfo[11]
        close_db()

        Session = sessionmaker(bind = engine)
        ses = Session()
        BadgedataDBss = ses.query(Badgedata).filter(Badgedata.id == id).one()

        #以下、スプレッドシートの情報とDBの情報が合致していなかったらDBに更新させる。（一つでも更新されていれば、全体のポイント数を更新するようにする。）
        if receivePt_zentai_ss != receivePt_zentai or receivePt_discuss_ss != receivePt_discuss or receivePt_discussLv1_ss != receivePt_discussLv1 or receivePt_discussLv2_ss != receivePt_discussLv2 or receivePt_discussLv2_ss != receivePt_discussLv2 or receivePt_hosuu_ss != receivePt_hosuu or receivePt_hosuuLv1_ss != receivePt_hosuuLv1 or receivePt_hosuuLv2_ss != receivePt_hosuuLv2 or receivePt_ritakoui_ss != receivePt_ritakoui or receivePt_ritakouiLv1_ss != receivePt_ritakouiLv1 or receivePt_ritakouiLv2_ss != receivePt_ritakouiLv2:
            BadgedataDBss.receivePt_zentai = receivePt_zentai_ss
            BadgedataDBss.receivePt_discuss = receivePt_discuss_ss
            BadgedataDBss.receivePt_discussLv1 = receivePt_discussLv1_ss
            BadgedataDBss.receivePt_discussLv2 = receivePt_discussLv2_ss
            BadgedataDBss.receivePt_hosuu = receivePt_hosuu_ss
            BadgedataDBss.receivePt_hosuuLv1 = receivePt_hosuuLv1_ss
            BadgedataDBss.receivePt_hosuuLv2 = receivePt_hosuuLv2_ss
            BadgedataDBss.receivePt_ritakoui = receivePt_ritakoui_ss
            BadgedataDBss.receivePt_ritakouiLv1 = receivePt_ritakouiLv1_ss
            BadgedataDBss.receivePt_ritakouiLv2 = receivePt_ritakouiLv2_ss

        ses.add(BadgedataDBss)
        ses.commit()
        ses.close()

@app.route('/UpdateDB', methods=['GET'])
def UpdateDB_GET():
    UpdateDB()

    return render_template('UpdateDB.html')

##スプレッドシートの情報をDBにアップデートする関数

#外部公開したい場合は下のapp.runを使用する。ローカルでテストで走らせたいだけの場合は上のapp.runを使用する。
if __name__ == '__main__':
    app.run()
    #app.run(debug=False, host='0.0.0.0', threaded=True, port=50009)
