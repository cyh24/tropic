#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
import random
import datetime

def banji_course(request):
    msg = init_msg(request)
    if request.GET.has_key('video-id'):
        try:
            video_id = int(request.GET['video-id'])
            video = Video.objects.get(id=video_id)
            if not video and not video.is_customize:
                 return render_to_response('videos/play-error.html', msg)

            current_num = 0
            if request.GET.has_key('current'):
                current_num = int(request.GET['current'])

            if video.is_reverse == 1:
                files = video.files.all()[::-1]
            else:
                files = video.files.all()
            if getLen(files) <= current_num:
                current_num = 0

            key = files[current_num].key
            video_url = Qiniu.download_private_url(key.encode('utf-8'))
            msg['video_url'] = video_url
            play_list = [val for val in files]

            if getLen(play_list) == 0 or play_list[0].chapter_num == -1:
                chapter_idx = []
            else:
                chapter_idx = [[0, play_list[0].chapter_name, play_list[0].chapter_num]]

            for i in range(1, getLen(play_list)):
                if play_list[i].chapter_num != -1 and play_list[i].chapter_num != play_list[i-1].chapter_num:
                    chapter_idx.append([i, play_list[i].chapter_name, play_list[i].chapter_num])

            chapter_idx.reverse()

            for i in range(getLen(play_list)):
                play_list[i].num = i
                play_list[i].cur_flag = 0

            play_list[current_num].cur_flag = 1

            for idx in chapter_idx:
                chapter = {}
                chapter['is_chapter'] = True
                chapter['chapter_num'] = idx[2]
                chapter['chapter_name'] = idx[1]
                play_list.insert(idx[0], chapter)

            msg['play_list'] = play_list

            return render_to_response('banji/banji_course.html', msg)
        except Exception, e:
            print "banji_course:", str(e)

    return render_to_response('videos/play-error.html', msg)

def courses(request):
    msg = init_msg(request)
    try:
        msg['cur_page'] = 0
    except Exception, e:
        print "banji_courses:", str(e)

    return render_to_response('banji/courses.html', msg)

@super_user
def upload_banji_course_ui(request):
    msg = init_msg(request)

    return render_to_response('banji/upload_banji_course.html', msg)

def upload_banji_course_post(request):
    pass
