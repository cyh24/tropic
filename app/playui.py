#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *


@login_required(login_url='/wechat-login/')
@csrf_protect
def watch_history_add(request):
    json = {'state': 'fail'}
    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            # add the watch number
            video = Video.objects.filter(id=video_id).all()
            if video != None:
                video = video[0]
                if add_user_watch_info(request, video) == True:
                    add_watch_num(video_id)
                    add_watch_history(request.user, video)
                    json['state'] = 'ok'

        except Exception, e:
            pass

    return JsonResponse(json)


def add_course_watch(user, video, current_num):
    try:
        course_progress = get_course_progress(user, video)
        if course_progress:
            course_progress.set_qfile_status_watched(current_num)
    except Exception as e:
        print "add_course_watch:", str(e)

from card_pro import membership_card
def play_ui(request):
    # f = open("video_url.txt", "w")
    # videos = Video.objects.all()
    # for video in videos:
        # files = video.files.all()
        # for file in files:
            # key = file.key
            # video_url = Qiniu.download_private_url(key.encode('utf-8'))
            # f.write(str(file.key)+ " " + video_url + "\n")
    # f.close()
    # files = QiniuFile.objects.all()
    # f = open("video_url.txt", "w")
    # for file in files:
        # key = file.key
        # video_url = Qiniu.download_private_url(key.encode('utf-8'))
        # f.write(str(file.id)+ " " + video_url + "\n")
    # f.close()

    # f = open('duration.txt')
    # data = f.readlines()
    # f.close()
    # for line in data:
        # line = line[:-1].split()
        # if len(line) == 2:
            # print(line

    if 'MCM' in request.GET:
        if int(request.GET['MCM']) == 1:
            return membership_card(request)

    msg = init_msg(request)
    msg['intrest_videos'] = get_intrest_videos()
    msg['nickname'] = "NONE_USER"
    if request.GET.has_key('video-id'):
        try:
            video_id = int(request.GET['video-id'])
            video = Video.objects.filter(id=video_id).all()
            if video != None:
                video = video[0]
                msg['video'] = video
            else:
                 return render_to_response('videos/play-error.html', msg)

            current_num = 0
            if request.GET.has_key('current'):
                try:
                    current_num = int(request.GET['current'])
                except Exception as e:
                    current_num = 0


            if video.is_reverse == 1:
                files = video.files.all()[::-1]
            else:
                files = video.files.all()
            if getLen(files) <= current_num:
                current_num = 0

            key = files[current_num].key
            video_url = Qiniu.download_private_url(key.encode('utf-8'))
            try:
                if video.upload_file:
                    msg['download_url'] = Qiniu.download_private_url(video.upload_file.encode('utf-8'))
            except Exception as e:
                print("download url:", str(e))
            msg['qfile'] = files[current_num]
            msg['video_url'] = video_url
            play_list = [val for val in files]

            if getLen(play_list) == 0 or play_list[0].chapter_num == -1:
                chapter_idx = []
            else:
                chapter_idx = [[0, play_list[0].chapter_name]]

            for i in range(1, getLen(play_list)):
                if play_list[i].chapter_num != -1 and play_list[i].chapter_num != play_list[i-1].chapter_num:
                    chapter_idx.append([i, play_list[i].chapter_name])

            chapter_idx.reverse()

            for i in range(getLen(play_list)):
                play_list[i].num = i
                play_list[i].cur_flag = 0

            play_list[current_num].cur_flag = 1

            for idx in chapter_idx:
                chapter = {}
                chapter['is_chapter'] = True
                chapter['chapter_name'] = idx[1]
                play_list.insert(idx[0], chapter)

            msg['play_list'] = play_list

            # add the watch number
            #add_watch_num(video_id)

            try:
                account = get_account_from_user(request.user)
                msg['nickname'] = account.nickname
            except Exception, e:
                pass

            try:
                # get the video's comments
                comments = Video.objects.filter(id=video_id)[0].comments.all().order_by('release_date')
                new_comments = []
                if getLen(comments) > 0:
                    for cc in comments:
                        cc.release_date = str(cc.release_date).split(' ')[0]
                        new_comments.append(cc)

                msg['comments'] = new_comments
                msg['comments_num'] = getLen(comments)
            except Exception, e:
                printError("play_ui: " + str(e))


            # check whether need pay for the play
            is_paid = get_video_state(request.user, video)

            # add customize course watch.
            add_course_watch(request.user, video, current_num)

            if video.is_customize == True and not is_paid:
                if checkMobile(request):
                    return render_to_response('mobile/videos/play-prohibited.html', msg)
                else:
                    return render_to_response('videos/play-prohibited.html', msg)

            #add_watch_history(request.user, video)

            if if_video_collected(request.user, video):
                msg['collect_state'] = '1'
            else:
                msg['collect_state'] = '0'

            if (video.money <= 0) or (is_paid):
                # add user watch log
                #add_user_watch_info(request, video)

                if checkMobile(request):
                    return render_to_response('mobile/videos/play.html', msg)
                else:
                    return render_to_response('videos/play.html', msg)
            else:
                if checkMobile(request):
                    return render_to_response('mobile/videos/play-prohibited.html', msg)
                else:
                    return render_to_response('videos/play-prohibited.html', msg)

        except Exception, e:
            print "play_ui: ", str(e)

    return render_to_response('videos/play-error.html', msg)


# @login_required(login_url='/wechat-login/')
@unlogin_user
@csrf_exempt
def play_ui_auth(request):
    msg = init_msg(request)
    msg['intrest_videos'] = get_intrest_videos()
    msg['nickname'] = "NONE_USER"
    if request.GET.has_key('video-id'):
        try:
            video_id = int(request.GET['video-id'])
            video = Video.objects.filter(id=video_id).all()
            if video != None:
                video = video[0]
                msg['video'] = video
            else:
                 return render_to_response('videos/play-error.html', msg)

            current_num = 0
            if request.GET.has_key('current'):
                current_num = int(request.GET['current'])

            files = video.files.all()
            if getLen(files) <= current_num:
                current_num = 0

            key = files[current_num].key
            video_url = Qiniu.download_private_url(key.encode('utf-8'))
            msg['video_url'] = video_url
            play_list = files
            for i in range(getLen(play_list)):
                play_list[i].num = i
                play_list[i].cur_flag = 0

            play_list[current_num].cur_flag = 1
            msg['play_list'] = play_list

            # add the watch number
            #add_watch_num(video_id)

            account = get_account_from_user(request.user)
            msg['nickname'] = account.nickname

            try:
                # get the video's comments
                comments = Video.objects.filter(id=video_id)[0].comments.all().order_by('release_date')
                new_comments = []
                if getLen(comments) > 0:
                    for cc in comments:
                        cc.release_date = str(cc.release_date).split(' ')[0]
                        new_comments.append(cc)

                msg['comments'] = new_comments
                msg['comments_num'] = getLen(comments)
            except Exception, e:
                printError("play_ui: " + str(e))


            # check whether need pay for the play
            is_paid = get_video_state(request.user, video)

            if video.is_customize == True and not is_paid:
                if checkMobile(request):
                    return render_to_response('mobile/videos/play-prohibited.html', msg)
                else:
                    return render_to_response('videos/play-prohibited.html', msg)

            # add customize course watch.
            if is_paid and request.user:
                add_course_watch(request.user, video, current_num)

            #add_watch_history(request.user, video)

            if if_video_collected(request.user, video):
                msg['collect_state'] = '1'
            else:
                msg['collect_state'] = '0'

            if (video.money <= 0) or (is_paid):
                # add user watch log
                #add_user_watch_info(request, video)

                if checkMobile(request):
                    return render_to_response('mobile/videos/play.html', msg)
                else:
                    return render_to_response('videos/play.html', msg)
            else:
                if checkMobile(request):
                    return render_to_response('mobile/videos/play-prohibited.html', msg)
                else:
                    return render_to_response('videos/play-prohibited.html', msg)

        except Exception, e:
            print "play_ui: ", str(e)

    return render_to_response('videos/play-error.html', msg)


def voteup(request):
    json = {}

    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            add_like_num(video_id)
        except Exception, e:
            printError(e)

    return JsonResponse(json)

def collect(request):
    json = {}

    if request.GET.has_key('video_id'):
        try:
            video_id = int(request.GET['video_id'])
            collect_state = request.GET['collect_state']
            if collect_state == '1':
                if cancle_collect_video(request.user, video_id) == True:
                    json['collect_state'] = '0'
                else:
                    json['collect_state'] = '1'
            elif collect_state == '0':
                if add_collect_video(request.user, video_id) == True:
                    json['collect_state'] = '1'
                else:
                    json['collect_state'] = '0'
        except Exception, e:
            printError(e)

    return JsonResponse(json)

@login_required(login_url='/wechat-login/')
@csrf_protect
def comment_add(request):
    json = {}
    try:
       add_comment(request)

    except Exception, e:
        printError(e)

    return JsonResponse(json)

@login_required(login_url='/wechat-login/')
@csrf_protect
def comment_delete(request):
    json = {}
    try:
        del_comment(request)

    except Exception, e:
        printError(e)

    return JsonResponse(json)

@login_required(login_url='/wechat-login/')
@csrf_protect
def pay_ui(request):
    msg = init_msg(request)
    try:
        kwargs = {}
        account = get_account_from_user(request.user)
        if account != None:
            #kwargs['account'] = account
            kwargs['id'] = request.GET['unpay_order_id']

            unpay_order = Order.objects.filter(**kwargs)
            msg ['unpay_order'] = unpay_order[0]

    except Exception, e:
        printError(e)

    return render_to_response('pay/pay.html', msg)


@login_required(login_url='/wechat-login/')
@csrf_protect
def ready_pay(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('video_id'):
            video_id = int(request.GET['video_id'])
            unpay_order = create_unpay_order(request.user, video_id)

            if unpay_order != None:
                if unpay_order.pay_state == 1:
                    json['state'] = 'ok'
                    json['order_id'] = unpay_order.id
                    json['order_price'] = unpay_order.price
                    json['pay_url'] = HOMEPAGE + "/pay?unpay_order_id=" + str(unpay_order.id)
                elif unpay_order.pay_state == 2:
                    json['state'] = 'paid'

    except Exception, e:
        printError("ready_pay: " + str(e))

    return JsonResponse(json)


