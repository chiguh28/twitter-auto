"""ID,PWの設定を管理する

     * JSONファイルを使用して管理する

Todo:
    * IDとPWをJSONに書き込む
    * JSONからIDとPWを取得する

"""

import json

class mngSetting():
    """設定管理クラス

     ID、PWをJSONから読み書きできるクラス

    Attributes:
        user_id: twitterのユーザーID
        user_pw: twitterのユーザーPW


    """
    def __init__(self):
        """初期メソッド

         最初に実行するメソッド
         各属性を初期化(空文字列)しておく

        Args:

        Returns:
           戻り値の型: 戻り値の説明 (例 : True なら成功, False なら失敗.)

        Raises:
            例外の名前: 例外の説明 (例 : 引数が指定されていない場合に発生 )

        Yields:

        Examples:


        Note:

        """ 
        self.user_id = ''
        self.user_pw = ''
    
    def saveToJson(self,id,pw):
        """JSONに保存するメソッド

         idとpwをJSONに書き込む
         JSONに書き込む際は辞書型にする必要がある


        Args:
            id: ユーザーID
            pw: ユーザーパスワード

        Returns:
           

        Raises:
            

        Yields:
           

        Examples:

        Note:

        """
        self.user_id = id
        self.user_pw = pw
        dictAccount ={'user_id':self.user_id,'user_pw':self.user_pw}

        fw = open('setting.json','w')

        json.dump(dictAccount,fw,indent=3)

    def loadFromJson(self):
        """JSONから読み込む

         idとpwをJSONから読み込む
         


        Args:
            id: ユーザーID
            pw: ユーザーパスワード

        Returns:
           

        Raises:
            

        Yields:
           

        Examples:

        Note:

        """
        fr = open('setting.json','r')

        dictAccount = json.load(fr)
        
        self.user_id = dictAccount['user_id']
        self.user_pw = dictAccount['user_pw']

        return [self.user_id,self.user_pw]

