#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
from views import wx_login_do

def index(request):
    try:
        wechat_user = WxAuth.get_user(request)

        if wechat_user != None:
            print "Wechat-User: ", wechat_user

            if check_wx_unionid(request, wechat_user) == True:
                wx_login_do(request, wechat_user)
                return HttpResponseRedirect('/space/')
        else:
            print "Wechat-User: None."

        try:
            vid = request_get_vid(request)
            if vid != None:
                vid = int(vid)
                from playui import play_ui
                import copy
                request_new = copy.copy(request)
                mutable = request_new.GET._mutable
                request_new.GET._mutable = True
                request_new.GET['video-id'] = vid
                request_new.GET._mutable = mutable
                return play_ui(request_new)
        except Exception, e:
            print "index", str(e)

        index_info = IndexInfo.objects.all()
        msg = init_msg(request)
        msg['index_info'] = index_info

    except Exception, e:
        printError(e)

    if checkMobile(request):
        return videos_ui(request)
        #return render_to_response('mobile/index.html', msg)
    else:
        return render_to_response('index.html', msg)

def mobile_index(request):
    try:
        wechat_user = WxAuth.get_user(request)

        if wechat_user != None:
            print "Wechat-User: ", wechat_user

            if check_wx_unionid(request, wechat_user) == True:
                wx_login_do(request, wechat_user)
        else:
            print "Wechat-User: None."

    except Exception, e:
        printError(e)

    msg = init_msg(request)


    if checkMobile(request):
        return render_to_response('mobile/index.html', msg)
    else:
        return render_to_response('index.html', msg)

def videos_ui(request):

    msg = init_msg(request)

    videos = Video.objects.all()
    # videos = Video.objects.filter(is_customize=False).all()
    videos, msg = get_catalog_videos(request, videos, msg)
    videos, msg = get_order_videos(request, videos, msg)

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


    get_content = "/videos/?"
    for key in request.GET:
        if key != "page":
            get_content += "%s=%s&"%(key, request.GET[key])
    msg['get_content'] = get_content

    msg['intrest_videos'] = get_intrest_videos()

    if checkMobile(request):
        return render_to_response('mobile/videos/videos.html', msg)
    else:
        return render_to_response('videos/videos.html', msg)



def search_result(request):

    msg = init_msg(request)

    try:
        #videos, msg = get_order_videos(request, msg)
        videos = get_search_videos(request)
        videos, msg = get_catalog_videos(request, videos, msg)
        videos, msg = get_order_videos(request, videos, msg)

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

        get_content = "/search/?"
        for key in request.GET:
            if key != "page":
                get_content += "%s=%s&"%(key, request.GET[key])
        msg['get_content'] = get_content

        msg['intrest_videos'] = get_intrest_videos()
    except Exception, e:
        print "search_result: ", e


    if checkMobile(request):
        return render_to_response('mobile/videos/search_result.html', msg)
    else:
        return render_to_response('videos/search_result.html', msg)
