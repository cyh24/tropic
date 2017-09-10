#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.db import transaction
from common import *
from models import *
from db_pro import *

def watch_status_update(request):
    try:
        with transaction.atomic():
            qfile_id = int(request.GET['qfile_id'])
            video_id = int(request.GET['video_id'])
            current_time = float(request.GET['current_time'])
            duration = float(request.GET['duration'])
            account = get_account_from_user(request.user)
            print(current_time, duration)
            video = get_video_by_id(video_id)
            q_file = QiniuFile.objects.get(id=qfile_id)

            # watch_video_status = WatchVideoStatus.objects.filter(account=account, video=video).all()
            # if getLen(watch_video_status) >= 1:
                # watch_video_status = watch_video_status[0]
            # else:
            watch_video_status = create_watch_video_status(account, video)

            watch_file_status = WatchFileStatus.objects.get(account=account, q_file=q_file)
            watch_file_status.duration = duration
            watch_file_status.current_time = max(watch_file_status.current_time, current_time)
            watch_file_status.save()

            watch_video_status.save()
    except Exception as e:
        print(e)
    return JsonResponse({})
