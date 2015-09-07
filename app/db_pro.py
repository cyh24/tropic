#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response 
from django.template import RequestContext 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.csrf import csrf_protect 
from django.template.context_processors import csrf
from django.template import loader

from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from django.db import transaction


from models import *
import time
import os
import sys

from common import *
from config import *

LOGO_FOLD = "app/static/storage/logo-images/"

def upload_post(request):
    if request.method == "POST":
        for x in request.POST:
            print x, request.POST[x]

    if request.FILES.has_key('logo'):
        path = LOGO_FOLD + getRandomStr() + "-" + request.FILES['logo'].name
        handle_uploaded_photo(path, request.FILES['logo'])
        print "logo: ", path

    try:
        path_logo = path[3:]
        if save_video(request, path_logo) == True:
            return HttpResponse("OK.") 
        else:
            return HttpResponse("Fail.") 
    except Exception, e:
        print str(e)
        return HttpResponse("Fail.") 
    
    return HttpResponse("OK") 


def save_tag(tag_name):
    print "save tag: ", tag_name
    db_tags = Tag.objects.all()
    db_tlist = []
    if db_tags != None:
        for db_tag in db_tags:
            db_tlist.append(db_tag.name)
    
    if db_tlist == None:
        pass
    elif tag_name in db_tlist:
        return None

    tag = Tag()
    tag.name = tag_name.encode('utf-8')
    tag.save()

    return True
    
def save_kind(kind_name):
    print "save kind; ", kind_name
    db_kinds = Tag.objects.all()
    db_klist = []
    if db_kinds != None:
        for db_kind in db_kinds:
            db_klist.append(db_kind.name)

    if db_klist == None:
        pass
    elif kind_name in db_klist:
        return False

    kind = Kind()
    kind.name = kind_name.encode('utf-8')
    kind.save()

    return True

def tag_deal(tag_list):
    db_tags = Tag.objects.all()
    db_tlist = []
    if db_tags != None:
        for db_tag in db_tags:
            db_tlist.append(db_tag.name)

    if tag_list == None:
        return True

    for tag in tag_list:
        if tag not in db_tlist:
            save_tag(tag)
            
def kind_deal(kind):
    db_kinds = Kind.objects.all()
    db_klist = []
    if db_kinds != None:
        for db_kind in db_kinds:
            db_klist.append(db_kind.name)
    if kind not in db_klist:
        save_kind(kind)

def get_video_by_id(video_id):
    try:
        video_id = int(video_id)
        video = Video.objects.filter(id=video_id).all()
        if video != None:
            video = video[0]
            return video
    except Exception, e:
        printError(e)

    return None

def save_video(request, logo_path, need_authority=True):
    video = Video()
    video.bucket = BUCKET_NAME
    video.domain = DOMAIN
    video.need_authority = need_authority
    video.logo_img = logo_path

    video.teacher = Account.objects.filter(user=request.user).all()[0]

    data = request.POST
    if data.has_key('title'):
        video.title = data['title'].encode('utf-8')
    if data.has_key('tag'):
        tagStr = data['tag']
        tag_list = tagStr.split()
        tag_len = get_len(tag_list)
        for i in range(tag_len):
            if i != 0:
                tagStr += " " + tag_list[i]
            else:
                tagStr += tag_list[i]
        video.tags_str = tagStr.encode('utf-8')
        tag_deal(tag_list)
        
    if data.has_key('kind'):
        kind = data['kind']
        video.kind_str = kind.encode('utf-8')
        kind_deal(kind)
    if data.has_key('key'):
        video.key = data['key'].encode('utf-8')
    if data.has_key('logo'):
        video.logo_img = data['logo'].encode('utf-8')
    if data.has_key('desc'):
        video.info = data['desc'].encode('utf-8')
    if data.has_key('money'):
        video.money = float(data['money'].encode('utf-8'))
    if data.has_key('minute'):
        video.video_time = int(data['minute'].encode('utf-8'))

    try:
        video.save()
        return True
    except Exception, e:
        print str(e)
        return False

def add_watch_num(video_id):
    try:
        video = Video.objects.filter(id=video_id).all()
        if video != None:
            video = video[0]
            video.watch_num += 1
            video.save()
    except Exception, e:
        print "Error: add_watch_num.\nError: " + str(e)


def get_interest_videos():
    try:
        videos = Video.objects.order_by('release_date')
        if get_len(videos) > 4:
            return videos[:4]
        return videos
    except Exception, e:
        print str(e)
    return None


def get_search_videos(request):
    try:
        if request.GET.has_key('title'):
            q_title = request.GET['title'].encode('utf8')
            videos = Video.objects.filter( title__icontains=q_title).all()
            return videos

    except Exception, e:
        printError(e)

    return None


def get_order_videos(request, videos, msg):
    try:
        if request.GET.has_key('order_by'):
            order_by = request.GET['order_by']
            msg['cur'] = order_by
            if order_by == "new":
                order_key = 'release_date'
            elif order_by == "like":
                order_key = '-like_num'
            elif order_by == "popular":
                order_key = '-watch_num'
            elif order_by == "price":
                flag = request.GET['flag']
                if flag == "up":
                    msg['up_down'] = "down"
                    order_key = '-money'
                else:
                    msg['up_down'] = "up"
                    order_key = 'money'
            else:
                order_key = 'release_date'
            m_videos = videos.order_by(order_key)

            return m_videos, msg

    except Exception, e:
        printError(e)

    m_videos = videos.order_by('release_date')
    return m_videos, msg



def add_like_num(video_id):
    try:
        video = Video.objects.filter(id=video_id).all()
        if video != None:
            video = video[0]
            video.like_num += 1
            video.save()
    except Exception, e:
        printError("Error: add_watch_num.\nError: " + str(e))

def if_video_collected(user, video):
    try:
        if user == None:
            return False
        account = get_account_from_user(user)
        collect_videos = get_collect_from_account(account)
        if collect_videos == None:
            return False
        else:
            videos = collect_videos.videos.all()
            if get_len(videos) < 1:
                return False
            for v in videos:
                if v == video:
                    return True

    except Exception, e:
        printError(e)

    return False

def add_collect_video(user, video_id):
    try:
        account = get_account_from_user(user)
        if account == None:
            return False

        collect_videos = get_collect_from_account(account)
        video = get_video_by_id(video_id)
        videos = collect_videos.videos.all()
        if get_len(videos) < 1:
            collect_videos.videos.add(video)
        else:
            is_exist = False
            for v in videos:
                if v == video:
                    is_exist = True
            if is_exist == False:
                collect_videos.videos.add(video)
            
        collect_videos.save()
        return True

    except Exception, e:
        printError("Error: add_watch_num.\nError: " + str(e))
    
    return False

def cancle_collect_video(user, video_id):
    try:
        account = get_account_from_user(user)
        if account == None:
            return False

        collect_videos = get_collect_from_account(account)
        video = get_video_by_id(video_id)
        videos = collect_videos.videos.all()
        
        if get_len(videos) < 1:
            return True
        else:
            t_videos = []
            for v in videos:
                if v != video:
                    t_videos.append(v)
            collect_videos.videos = t_videos
            
        collect_videos.save()
        return True

    except Exception, e:
        printError("Error: cancle_collect_video.\nError: " + str(e))
    
    return False


def add_comment(request):
    json = {}
    try:
        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])
        if request.GET.has_key('follow_id'):
            follow_id = int(request.GET['follow_id'])
        if request.GET.has_key('content'):
            content = request.GET['content'].encode('utf-8')
        print video_id, follow_id, content

        comment = Comment()
        comment.user = Account.objects.filter(user=request.user).all()[0]
        comment.follow_id = follow_id
        comment.comment    = content

        comment.save()

        video = get_video_by_id(video_id)
        video.comments.add(comment)
        video.save()

    except Exception, e:
        printError(e)

def create_account_given_wx(wx_user):
    try:
        open_id = wx_user['openid']
        with transaction.atomic():
            user = User()
            user.username = open_id
            user.set_password("Z!"+open_id+"1!")
            user.save()
        
            account = Account()
            account.user = user
            account.openid = open_id
            account.user_pic = wx_user['headimgurl']
            sex = wx_user['sex']
            try:
                sex = int(sex)
                if sex != 0 and sex != 1:
                    sex = -1
            except Exception, e:
                sex = -1
                printError(e)
            account.sex = sex
            account.info = "这家伙很懒，什么都没留~"

            account.save()
            return True
    except Exception, e:
        printError(e)

    return False

def create_account_given_user(user):
    try:
        account = Account()
        account.user = user
        account.nickname = user.username
        account.user_pic = "/static/samples/boy/junyong02.jpg"

        account.info = "这家伙很懒，什么都没留~"

        account.save()
        return account
    except Exception, e:
        printError(e)

    return None


def check_wx_openid(wx_user):
    try:
        openid = wx_user['openid']
        account = Account.objects.filter(openid=openid).all()

        if get_len(account) < 1:
            create_account_given_wx(wx_user)
            return True
        else:
            account = account[0]
            return True

    except Exception, e:
        printError(e)

    return False

def exist_user_account(user):
    try:
        account = Account.objects.filter(user=user).all()

        if get_len(account) < 1:
            create_account_given_user(user)
            return True

    except Exception, e:
        printError(e)

    return False


def get_account_from_user(user):
    account = None
    try:
        account = Account.objects.filter(user=user).all()
        if get_len(account) < 1:
            account = create_account_given_user(user)
        else:
            account = account[0]
    except Exception, e:
        printError(e)

    return account


def create_collect_given_account(account):
    if account == None:
        return None
    collect_videos = None
    try:
        collect_videos = CollectVideos()
        collect_videos.account = account
        collect_videos.save()
    except Exception, e:
        printError(e)

    return collect_videos

def get_collect_from_account(account):
    if account == None:
        return None
    collect_videos = None
    try:
        collect_videos = CollectVideos.objects.filter(account=account).all()
        if get_len(collect_videos) < 1:
            collect_videos = create_collect_given_account(account)
        else:
            collect_videos = collect_videos[0]

    except Exception, e:
        printError(e)

    return collect_videos


def add_watch_history(user, video):
    if user == None:
        return False
    try:
        account = get_account_from_user(user)
        if account == None:
            return False

        watch_history = WatchHistory.objects.filter(account=account).all()
        if get_len(watch_history) < 1:
            watch_history = WatchHistory()
            watch_history.account = account
            watch_history.save()
        else:
            watch_history = watch_history[0]

        videos = watch_history.videos.all()
        if get_len(videos) < 1:
            watch_history.videos.add(video)
        else:
            is_exist = False
            for v in videos:
                if v == video:
                    is_exist = True
                    break
            if is_exist == False:
                print "add watch history."
                watch_history.videos.add(video)

        watch_history.save()
        return True

    except Exception, e:
        printError(e)

    return False


def get_watch_history(user):

    if user == None:
        return None, 0
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        watch_history = WatchHistory.objects.filter(account=account).all()
        if get_len(watch_history) < 1:
            return None, 0
        else:
            watch_history = watch_history[0]

        videos = watch_history.videos.all()
        
        return videos, watch_history.videos_num

    except Exception, e:
        printError(e)

    return None, 0


def get_watch_history_num(user):
    try:
        account = get_account_from_user(user)
        watch_history = WatchHistory.objects.filter(account=account).all()[0]
        return watch_history.videos_num

    except Exception, e:
        printError(e)

    return 0

def del_watch_history(user, video_id):
    try:
        account = get_account_from_user(user)
        watch_history = WatchHistory.objects.filter(account=account).all()[0]
        temp_video = get_video_by_id(video_id)
        watch_history.videos.remove(temp_video)
        watch_history.save()
    except Exception, e:
        printError(e)

    return False

def get_collect(user):

    if user == None:
        return None, 0
    try:
        account = get_account_from_user(user)
        if account == None:
            return None, 0

        collect_videos = CollectVideos.objects.filter(account=account).all()
        if get_len(collect_videos) < 1:
            return None, 0
        else:
            collect_videos = collect_videos[0]

        videos = collect_videos.videos.all()
        
        return videos, collect_videos.videos_num

    except Exception, e:
        printError(e)

    return None, 0

def get_collect_num(user):
    try:
        account = get_account_from_user(user)
        collect_videos = CollectVideos.objects.filter(account=account).all()[0]
        
        return collect_videos.videos_num

    except Exception, e:
        printError(e)

    return 0

def del_collect(user, video_id):
    try:
        account = get_account_from_user(user)
        collect_videos = CollectVideos.objects.filter(account=account).all()[0]
        temp_video = get_video_by_id(video_id)
        collect_videos.videos.remove(temp_video)
        collect_videos.save()
    except Exception, e:
        printError(e)

    return False



def get_unpay_num(user):
    try:
        account = get_account_from_user(user)
        unpay_order = Order.objects.filter(account=account).filter(pay_state=False).all()
        return get_len(unpay_order)
    except Exception, e:
        printError(e)

    return 0

def get_paid_num(user):
    try:
        account = get_account_from_user(user)
        paid_order = Order.objects.filter(account=account).filter(pay_state=True).all()
        return get_len(paid_order)
    except Exception, e:
        printError(e)

    return 0


def update_account(request):
    try:
        account = get_account_from_user(request.user)
        account.nickname = request.GET['nickname'].encode("utf-8")
        account.info     = request.GET['info'].encode("utf-8")
        account.sex      = int(request.GET['sex'])

        account.save()
        return True
    except Exception, e:
        printError(e)

    return False