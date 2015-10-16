#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *



@login_required(login_url='/login/')
@csrf_exempt
def play_ui(request):
    msg = init_msg(request)
    msg['intrest_videos'] = get_intrest_videos()
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
            add_watch_num(video_id)

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

            add_watch_history(request.user, video)

            if if_video_collected(request.user, video):
                msg['collect_state'] = '1'
            else:
                msg['collect_state'] = '0'

            if (video.money <= 0) or (is_paid):
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

@login_required(login_url='/login/')
@csrf_protect
def comment_add(request):
    json = {}
    try:
       add_comment(request)

    except Exception, e:
        printError(e)

    return JsonResponse(json)


@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
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
                    json['pay_url'] = HOMEPAGE + "/pay?unpay_order_id=" + str(unpay_order.id)
                elif unpay_order.pay_state == 2:
                    json['state'] = 'paid'

    except Exception, e:
        printError("ready_pay: " + str(e))

    return JsonResponse(json)


