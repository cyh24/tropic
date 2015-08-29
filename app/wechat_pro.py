from weixin.client import WeixinAPI, WeixinMpAPI
from config import *
from common import *

class WechatAuth():
    def __init__(self):
        scope = ("snsapi_login",)

        self.PC_api = WeixinAPI(appid = APP_ID, 
                                app_secret   = APP_SECRET,
                                redirect_uri = REDIRECT_URL)

        self.Mobile_api = WeixinMpAPI(appid = APP_ID, 
                                    app_secret   = APP_SECRET,
                                    redirect_uri = REDIRECT_URL)

        self.pc_auth_url     = self.PC_api.get_authorize_url(scope=scope)
        self.mobile_auth_url = self.Mobile_api.get_authorize_url(scope=scope)


    def get_authorize_url(self, request):
        if checkMobile(request) == True:
            return self.mobile_auth_url
        else:
            return self.pc_auth_url
        

    def get_user(self, request):
        try:
            code = ""
            if request.GET.has_key('code'):
                code = request.GET['code']
            else:
                return None

            if checkMobile(request) == True:
                auth_info = self.Mobile_api.exchange_code_for_access_token(code=code)
                userApi = WeixinMpAPI(access_token=auth_info['access_token'])
                user_info = userApi.user(openid=auth_info['openid'])
                return user_info
            else:
                auth_info = self.PC_api.exchange_code_for_access_token(code=code)
                userApi = WeixinAPI(access_token=auth_info['access_token'])
                user_info = userApi.user(openid=auth_info['openid'])
                return user_info
        except Exception, e:
            printError(e)

        return None

WxAuth = WechatAuth()

