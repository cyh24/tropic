#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *

from save_excel import *

from wxpay import *
from django.http import StreamingHttpResponse
 

def download(request):
    # do something...
    def file_iterator(file_name, chunk_size=1024):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    filename = "none"
    if request.GET.has_key("filename"):
        filename = request.GET['filename']
 
    the_file_name = DOWNLOAD_FOLD + filename
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
 
    return response

def test(request):
    print "TEST"
    msg = init_msg(request)
    save_history()

    return render_to_response('test.html', msg)


def login_ui(request):
    msg = init_msg(request)

    return render_to_response('login/login.html', msg)

def wechat_login(request):
    #login_url = "https://open.weixin.qq.com/connect/qrconnect?appid=%s&redirect_uri=%s&response_type=%s&scope=%s&state=%s#wechat_redirect"%(APP_ID, REDIRECT_URL, RESPONSE_TYPE, SCOPE, STATE)
    login_url = WxAuth.get_authorize_url(request)

    return HttpResponseRedirect(login_url)

def wechat_share(request):
    url = "http://facebuaa.cn"
    if request.GET.has_key('cur_url'):
        url = request.GET['cur_url']

    qrcode_url = get_qrcode(url)
    print qrcode_url
    json={'qrcode_url': qrcode_url}

    return JsonResponse(json)

def excute_login(request, username, password):
    try:
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                print "user pass."
    except Exception, e:
        printError(e)


def wx_login_do(request, user):
    username = user['unionid']
    password = "Z!"+username+"1!"

    excute_login(request, username, password)

    account = get_account_from_user(request.user)
    if checkMobile(request) == True:
        if account.wx_wx_openid == None or account.wx_wx_openid == "":
            account.wx_wx_openid = user['openid']
    else:
        if account.wx_pc_openid == None or account.wx_pc_openid == "":
            account.wx_pc_openid = user['openid']
    account.save()


def login_do(request):
    msg = init_msg(request)

    username = request.POST['username']
    password = request.POST['password']
    

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            print "user pass."

            # judge whether db exist accout related to the user.
            exist_user_account(user)

            if msg.has_key('next'):
                return HttpResponseRedirect( HOMEPAGE+ msg['next'])
            else:
                return HttpResponseRedirect( HOMEPAGE)


    return render_to_response('login/login.html', msg)

def log_out(request):
    logout(request)

    return HttpResponseRedirect(HOMEPAGE)

