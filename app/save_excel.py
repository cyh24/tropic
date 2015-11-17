#!/usr/bin/python
#-*- coding: utf-8 -*-
from models import *
import csv

def save_history():
    history = WatchHistory.objects.all()
    print history


def excel_videos():
    videos = Video.objects.all()
    if videos == None:
        return 0

    data = []
    for v in videos:
        row = []
        row.append(v.title)
        row.append(v.kind_str)
        row.append(v.tag_str)
        row.append(v.watch_num)
        row.append(v.collect_num)
        row.append(v.comment_num)




if __name__ == "__main__":
    get_history()
