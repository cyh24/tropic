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
    print "downloading..."
    # do something...
    def file_iterator(file_name, chunk_size=1024):
        print file_name
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    filename = "none"
    the_file_name = ""
    if request.GET.has_key("filename"):
        filename = request.GET['filename']
        if filename == "users.csv":
            the_file_name = users_info()
        elif filename == "videos.csv":
            the_file_name = videos_info()
        elif filename == "user_watch_info.csv":
            the_file_name = user_watch_info()
        elif filename == "user_order_info.csv":
            the_file_name = user_order_info()

    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(str(filename))

    return response


# @super_user
def tree(request):
    msg = init_msg(request)

    try:
        first_catalogs = get_all_first_catalogs()
        for first_cata in first_catalogs:
            second_catas = []
            for second_cata in first_cata.second_catalogs.all():
                second_catas.append(second_cata)
            first_cata.second_catalogs_list = second_catas
        msg['first_catalogs'] = first_catalogs
    except Exception as e:
        print("get all catalogs error:", str(e))

    videos = Video.objects.all()
    videos, msg = get_catalog_videos(request, videos, msg)
    # videos = Video.objects.filter(is_customize=False).all()
    videos, msg = get_order_videos(request, videos, msg)

    msg = get_study_time(get_account_from_user(request.user), videos, msg)
    total_page = (getLen(videos)+PAGE_SIZE-1)/PAGE_SIZE
    subVideos, cur_page = paginator_show(request, videos, PAGE_SIZE)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    try:
        cards = Card.objects.all()
        if cards:
            for i, video in enumerate(subVideos):
                for card in cards:
                    if video in card.videos.all():
                        subVideos[i].card = card
                        break
    except Exception as e:
        print "videos ui: ", e

    msg['videos']     = subVideos
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1
    msg['total_page'] = total_page


    get_content = "/test/?"
    for key in request.GET:
        if key != "page":
            get_content += "%s=%s&"%(key, request.GET[key])
    msg['get_content'] = get_content

    msg['intrest_videos'] = get_intrest_videos()

    if checkMobile(request):
        return render_to_response('mobile/test.html', msg)
    else:
        return render_to_response('tree.html', msg)

def test(request):
    msg = init_msg(request)

    try:
        first_catalogs = get_all_first_catalogs()
        for first_cata in first_catalogs:
            second_catas = []
            for second_cata in first_cata.second_catalogs.all():
                second_catas.append(second_cata)
            first_cata.second_catalogs_list = second_catas
        msg['first_catalogs'] = first_catalogs
    except Exception as e:
        print("get all catalogs error:", str(e))

    videos = Video.objects.all()
    videos, msg = get_catalog_videos(request, videos, msg)
    # videos = Video.objects.filter(is_customize=False).all()
    videos, msg = get_order_videos(request, videos, msg)

    msg = get_study_time(get_account_from_user(request.user), videos, msg)
    total_page = (getLen(videos)+PAGE_SIZE-1)/PAGE_SIZE
    subVideos, cur_page = paginator_show(request, videos, PAGE_SIZE)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    try:
        cards = Card.objects.all()
        if cards:
            for i, video in enumerate(subVideos):
                for card in cards:
                    if video in card.videos.all():
                        subVideos[i].card = card
                        break
    except Exception as e:
        print "videos ui: ", e

    msg['videos']     = subVideos
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1
    msg['total_page'] = total_page


    get_content = "/test/?"
    for key in request.GET:
        if key != "page":
            get_content += "%s=%s&"%(key, request.GET[key])
    msg['get_content'] = get_content

    msg['intrest_videos'] = get_intrest_videos()

    if checkMobile(request):
        return render_to_response('mobile/test.html', msg)
    else:
        return render_to_response('test.html', msg)

def login_ui(request):
    msg = init_msg(request)

    return render_to_response('login/login.html', msg)

def wechat_login(request):
    login_url = WxAuth.get_authorize_url(request)

    return HttpResponseRedirect(login_url)

def wechat_share(request):
    url = "http://el.tropic.com.cn"
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
                print "excute_login, user pass."
    except Exception, e:
        printError("excute_login: " + str(e))


def wx_login_do(request, user):
    print "wx_login_do..."
    username = user['unionid']
    password = "Z!"+username+"1!"

    excute_login(request, username, password)

    exist_user_account(request.user)
    #account = get_account_from_user(request.user)
    #if checkMobile(request) == True:
    #    if account.wx_wx_openid == None or account.wx_wx_openid == "":
    #        account.wx_wx_openid = user['openid']
    #else:
    #    if account.wx_pc_openid == None or account.wx_pc_openid == "":
    #        account.wx_pc_openid = user['openid']
    #account.save()


def login_do(request):
    msg = init_msg(request)

    username = request.POST['username']
    password = request.POST['password']


    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            print "login_do: user pass."

            # judge whether db exist accout related to the user.
            exist_user_account(user)

            if user.is_superuser == True:
                return HttpResponseRedirect("/manage/")

            if msg.has_key('next'):
                return HttpResponseRedirect( HOMEPAGE+ msg['next'])
            else:
                return HttpResponseRedirect(HOMEPAGE)


    return render_to_response('login/login.html', msg)

def log_out(request):
    logout(request)

    return HttpResponseRedirect(HOMEPAGE)

