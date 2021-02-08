import tweepy
from config import CONFIG
from TwitterOauth import TwitterOauth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import oauth2 as oauth
import json
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import schedule

class twitterApp(QThread):
    # twitterAPIを使用する設定
    # APPを起動した際に初期化
    MAX_COUNT = 60

    sendCount = pyqtSignal(int,int)
    sendFlag = pyqtSignal(bool,bool,bool)
    sendMessage = pyqtSignal(str)


    def __init__(self,host_window):
        
        super(twitterApp,self).__init__()
        self.CONSUMER_KEY = CONFIG["API_KEY"]
        self.CONSUMER_SECRET = CONFIG["API_SECRET_KEY"]
        self.twitterOauth = TwitterOauth(self.CONSUMER_KEY,self.CONSUMER_SECRET)
        self.api =''
        self.window = host_window
        self.follow_count = self.MAX_COUNT
        self.retweet_count = self.MAX_COUNT
        self.favorite_count = self.MAX_COUNT
        self.is_running = True
        self.favorite_time = datetime.datetime.now()
        self.retweet_time = datetime.datetime.now()
        self.follow_time = datetime.datetime.now()
        
    def run(self):
        """
        QThreadのrunメソッドのオーバーライド
        """
        self.autoWrapper(self.window.checkBox_4.isChecked(),self.window.lineEdit_4.text(),self.window.checkBox.isChecked(),self.window.checkBox_2.isChecked(),self.window.checkBox_3.isChecked(),self.window.spinBox.value())
    

    def login(self,login_id,password):
        """twitterにログイン

         twitterにログインするメソッド
         seleniumを利用してPINコードを取得→アクセストークンを取得する

        Args:
            login_id(str): twitterにログインするID @を付けること
            password : twitterにログインするPW

        Returns:
           user_name: twitterのユーザー名
           friends_count: フォロー数
           follower_count: フォロワー数
        Raises:
            

        Examples:

        Note:
            PINコードが表示される時間によってエラーが発生する

        """
        option = Options()
        option.add_argument('--headless')

        # 認証ページのURLを取得する
        authenticate_url = self.twitterOauth.get_authenticate_url()

        # driverを利用してログインする
        # driver = webdriver.Chrome(options=option)
        driver = webdriver.Chrome(options=option)
        driver.get(authenticate_url)
        time.sleep(3)

        # 画面に表示されたPINコードを取得する
        idForm = driver.find_element_by_id('username_or_email')
        idForm.send_keys(login_id)
        passForm = driver.find_element_by_id('password')
        passForm.send_keys(password)

        time.sleep(3)

        loginButton = driver.find_element_by_id('allow')
        loginButton.click()

        pinCode = int(driver.find_element_by_tag_name('code').text)

        #PINコードを基にアクセストークンを取得する
        access_token_content = self.twitterOauth.get_access_token_content(pinCode)
        access_token = access_token_content["oauth_token"][0]
        access_token_secret = access_token_content["oauth_token_secret"][0]


        auth = tweepy.OAuthHandler(self.CONSUMER_KEY,self.CONSUMER_SECRET)
        auth.set_access_token(access_token,access_token_secret)

        driver.close()
        #tweepyのAPIを取得する
        self.api = tweepy.API(auth)

        # アカウント情報を取得する
        user_me = self.api.me()

        return [user_me.name,user_me.friends_count,user_me.followers_count]

    
    #キーワード検索からtwitterの自動実行
    def autoRunFromKeyWordSearch(self,word,favorite,retweet,follow,seconds):
        """twitterキーワード検索から操作実行

         チェックをつけてある動作をキーワード検索に基づいて自動実行する

        Args:
            word: 検索キーワード
            favorite : いいねを実行するフラグ
            retweet: リツイートを実行するフラグ
            follow: フォローを実行するフラグ
            seconds: 実行間隔(s)

        Returns:

        Raises:
            

        Examples:

        Note:
        カウントが0になった時の時間の1時間後にカウントを回復させるようにする

        """
        self.sendMessage.emit('キーワード検索に対する自動実行を開始!')
        # self.outLog('キーワード検索に対する自動実行を開始!')
        
        search_results = self.api.search(q=word,count=self.MAX_COUNT)
        
        for result in search_results:

            # 指定時間を過ぎていれば回数を戻す処理
            time_now = datetime.datetime.now()
            if time_now >= self.favorite_time and self.favorite_count <= 0:
                self.favorite_count = self.MAX_COUNT
            if time_now >= self.retweet_time and self.retweet_count <= 0:
                self.retweet_count = self.MAX_COUNT
            if time_now >= self.follow_time and self.follow_count <= 0:
                self.follow_count = self.MAX_COUNT

            tweet_id = result.id
            user_id = result.user._json['id']

            if(favorite and self.favorite_count > 0):
                try:
                    self.api.create_favorite(tweet_id) 
                    self.favorite_count -= 1
                    # 回数が0になってからの時間を算出
                    if(self.favorite_count <= 0):
                        self.favorite_time = self.calcAfterOneHour()

                except Exception as e:
                    favorite = False
                    print(e)
            else:
                favorite = False
            if(retweet and self.retweet_count > 0):
                try:
                    self.api.retweet(tweet_id)      
                    self.retweet_count -= 1
                    # 回数が0になってからの時間を算出
                    if(self.retweet_count <= 0):
                        self.retweet_time = self.calcAfterOneHour()

                except Exception as e:
                    retweet = False
                    print(e)
            else:
                retweet = False
            if(follow and self.follow_count > 0):
                try:
                    self.api.create_friendship(user_id)
                    self.follow_count -= 1
                    # 回数が0になってからの時間を算出
                    if(self.follow_count <= 0):
                        self.follow_time = self.calcAfterOneHour()
                    
                except Exception as e:
                    follow = False
                    print(e)
            else:
                follow = False
            self.sendFlag.emit(retweet,favorite,follow)
            self.sendCount.emit(self.favorite_count,self.retweet_count)
            self.sendMessage.emit('処理を待機中です.停止するなら今のタイミングでお願いします.')
            QThread.sleep(seconds)
            if(not self.is_running):
                break
            if(self.favorite_count <=0 and self.retweet_count <= 0):
                self.stop()
        
        self.sendMessage.emit('キーワード検索に対する自動実行を終了!')
        self.window.changeBtnStatus(self.window.pushButton,self.window.pushButton_2)

    #タイムラインによるtwitterの自動実行
    def autoRunAgainstTimeLine(self,favorite,retweet,seconds):
        """twitterタイムラインに対して操作実行

         チェックをつけてある動作をタイムラインに基づいて自動実行する

        Args:
            favorite : いいねを実行するフラグ
            retweet: リツイートを実行するフラグ
            follow: フォローを実行するフラグ
            seconds: 実行間隔(s)

        """
        self.sendMessage.emit('フォロワーに対する自動実行を開始!')    

        # タイムラインのツイートを取得
        tl = self.api.home_timeline(count=self.MAX_COUNT)
        for tweet in tl:
            # 指定時間を過ぎていれば回数を戻す処理
            time_now = datetime.datetime.now()
            if time_now >= self.favorite_time and self.favorite_count <= 0:
                self.favorite_count = self.MAX_COUNT
            if time_now >= self.retweet_time and self.retweet_count <= 0:
                self.retweet_count = self.MAX_COUNT

            
            tweet_id = tweet.id
            if(favorite and self.favorite_count > 0):
                try:
                    self.api.create_favorite(tweet_id)
                    self.favorite_count -= 1
                    # 回数が0になってからの時間を算出
                    if(self.favorite_count <= 0):
                        self.favorite_time = self.calcAfterOneHour()
                    
                except Exception as e:
                    favorite = False
                    print(e)
            else:
                favorite = False
            if(retweet and self.retweet_count > 0):
                try:
                    self.api.retweet(tweet_id)
                    self.retweet_count -= 1
                    # 回数が0になってからの時間を算出
                    if(self.retweet_count <= 0):
                        self.retweet_time = self.calcAfterOneHour()
      
                except Exception as e:
                    retweet = False
                    print(e)
            else:
                retweet = False

            self.sendFlag.emit(retweet,favorite,False)
            self.sendCount.emit(self.favorite_count,self.retweet_count)
            self.sendMessage.emit('処理を待機中です.停止するなら今のタイミングでお願いします.')
            QThread.sleep(seconds)
            if(not self.is_running):
                break


        self.sendMessage.emit('フォロワーに対する自動実行を終了!')
        
        self.window.changeBtnStatus(self.window.pushButton,self.window.pushButton_2)

    def autoWrapper(self,is_tl,word,favorite,retweet,follow,seconds):
        """
        @概要
        自動実行する2つのメソッドのwrapper
        @param
        is_tl:タイムラインに対して自動実行するかのフラグ
        @param
        word:検索キーワード
        @param
        favorite:いいねフラグ
        @param
        retweet:リツイートフラグ
        @param
        follow:フォローフラグ
        @seconds:
        実行間隔フラグ
        """
        if(is_tl):
            self.autoRunAgainstTimeLine(favorite,retweet,seconds)
        if(word):
            self.autoRunFromKeyWordSearch(word,favorite,retweet,follow,seconds)
    
    

        
    def calcAfterOneHour(self):
        """
        @概要
        関数を実行してから1時間後の時間を算出する
        """
        dt_now = datetime.datetime.now()

        dt_hour = dt_now + datetime.timedelta(minutes=1)
        return dt_hour

            


        



