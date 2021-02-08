from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import MainWindow

import sys

from twitter import twitterApp
import concurrent.futures
from setting import mngSetting
import datetime

class MainWindow(QDialog,MainWindow.Ui_MainWindow):

    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)
        self.tw_app = twitterApp(self)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.setting = mngSetting()
        self.init_stylesheet = "background-color: rgb(167, 167, 167);"
        self.act_list = []
        self.thread = QThread()



    def loginTwitter(self):
        [user_name,follow_count,follower_count] = self.tw_app.login(self.lineEdit.text(),self.lineEdit_2.text())
        self.label_9.setText(user_name)
        self.label_10.setText(str(follow_count))
        self.label_11.setText(str(follower_count))

        # ログインを実行したらログインボタンを無効にする
        self.pushButton_5.setEnabled(False)
        self.changeBtnStyleSheet(self.pushButton_5,False)
        self.outLog('ログインに成功しました!')
        

    def autorun(self):
        # 自動実行が開始されたら自動実行ボタンをクリックできないようにする
        self.changeBtnStatus(self.pushButton_2,self.pushButton)
        self.tw_app.is_running = True

        
        self.tw_app.moveToThread(self.thread)

        # スレッドからの紐づけ
        self.tw_app.sendFlag.connect(self.outAction)
        self.tw_app.sendMessage.connect(self.outLog)
        self.tw_app.sendCount.connect(self.setCount)
        self.thread.started.connect(self.tw_app.run)

        self.thread.start()
        


    def stoprun(self):
        self.tw_app.is_running = False
        self.thread.terminate()
        print(self.thread.isRunning)
        self.outLog('処理を停止中です')
        # 処理を停止したら自動実行ボタンを有効にして停止ボタンを無効にする
        self.changeBtnStatus(self.pushButton,self.pushButton_2)
        
    def saveSetting(self):
        self.setting.saveToJson(self.lineEdit.text(),self.lineEdit_2.text())
        self.outLog('設定を保存しました!')

    def loadSetting(self):
        [id,pw] = self.setting.loadFromJson()
        self.lineEdit.setText(id)
        self.lineEdit_2.setText(pw)
        self.outLog('設定を読み込みました!')

    def changeBtnStyleSheet(self,btn,can):
        # ボタンのスタイルを変更する
        # 有効にする(can=true)場合は背景色を初期スタイルに戻す
        if can:
            btn.setStyleSheet(self.init_stylesheet)
        else:
            btn.setStyleSheet("background-color: rgb(0, 0, 0);")

    def changeBtnStatus(self,onBtn,offBtn):
        """
        @概要
        ボタンの状態を変更する

        @param onBtn
        有効にしたいボタンオブジェクト
        @param offBtn
        無効にしたいボタンオブジェクト
        """
        onBtn.setEnabled(True)
        self.changeBtnStyleSheet(onBtn,True)
        offBtn.setEnabled(False)
        self.changeBtnStyleSheet(offBtn,False)

    
    def outAction(self,rt,like,follow):
        if(rt):
            rt_act = 'RT'
        else:
            rt_act = '-'
        if(like):
            like_act = 'Like'
        else:
            like_act = '-'
        if(follow):
            follow_act = 'Follow'
        else:
            follow_act = '-'
        
        # action_listに今回作成したリストを追加していく
        tmp_list = [rt_act,like_act,follow_act,datetime.datetime.now()]

        self.act_list.append(tmp_list)

        # 行数を追加していく必要があるため
        # 行名は1から順に数字にしていく
        self.tableWidget.setRowCount(len(self.act_list))
        tmpHeaders = list(range(1,len(self.act_list)))
        verHeaders = [str(n) for n in tmpHeaders]
        self.tableWidget.setVerticalHeaderLabels(verHeaders)
        
        for n in range(len(self.act_list)):
            for m in range(len(tmp_list)):
                item = QTableWidgetItem(str(self.act_list[n][m]))
                self.tableWidget.setItem(n, m, item)

    def outLog(self,message):
        log_message = '[' + str(datetime.datetime.now()) + '] ' + message
        self.listWidget.addItem(log_message)

    def setCount(self,like_count,rt_count):
        self.label_14.setText(str(like_count))
        self.label_17.setText(str(rt_count))





if __name__ == "__main__":
    
    

    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()