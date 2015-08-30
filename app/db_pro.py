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
    video.teacher_name = "cyh"

    data = request.POST
    if data.has_key('title'):
        video.title = data['title'].encode('utf-8')
    if data.has_key('tag'):
        tagStr = data['tag']
        tag_list = tagStr.split()
        tag_len = len(tag_list)
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
        if len(videos) > 4:
            return videos[:4]
        return videos
    except Exception, e:
        print str(e)
    return None

def get_order_videos(request, msg):
    try:
        if request.GET.has_key('order_by'):
            order_by = request.GET['order_by']
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
            videos = Video.objects.order_by(order_key)

            return videos, msg

    except Exception, e:
        printError(e)

    videos = Video.objects.order_by('release_date')
    return videos, msg



def add_like_num(video_id):
    try:
        video = Video.objects.filter(id=video_id).all()
        if video != None:
            video = video[0]
            video.like_num += 1
            video.save()
    except Exception, e:
        printError("Error: add_watch_num.\nError: " + str(e))


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
        comment.user_name = "cyh"
        comment.user_pic  = "http://ask.julyedu.com/uploads/avatar/000/00/07/70_avatar_min.jpg"
        comment.follow_id = follow_id
        comment.comment    = content

        comment.save()

        video = get_video_by_id(video_id)
        video.comments.add(comment)
        video.save()

    except Exception, e:
        printError(e)

def create_account(wx_user):
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


def check_wx_openid(user):
    try:
        openid = user['openid']
        account = Account.objects.filter(openid=openid).all()

        if len(account) < 1:
            create_account(user)
            return True
        else:
            account = account[0]
            return True

    except Exception, e:
        printError(e)

    return False



