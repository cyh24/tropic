#!/usr/bin/python
#-*- coding: utf-8 -*-
from models import *
import csv
from config import DOWNLOAD_FOLD
import xlwt
from common import getRandomStr, getLen
from db_pro import get_unpay_num, get_paid_num, get_watch_history_num, get_collect_num
import datetime

def users_info():
    try:
        title_name_ = "users.xls"
        accounts = Account.objects.all()
        row_title = ["id", "昵称", "性别", 
                "个性签名", "购买数量", "收藏数量","购物车数量", "上次登陆时间"]
        data = []
        data.append(row_title)
        if getLen(accounts) > 0:
            for acc in accounts:
                row = []
                row.append(acc.id)
                row.append(acc.nickname)
                row.append(acc.sex)
                row.append(acc.info)
                row.append(get_paid_num(acc.user))
                row.append(get_collect_num(acc.user))
                row.append(get_unpay_num(acc.user))
                row.append(str(acc.user.last_login).split('+')[0])

                data.append(row)

        filepath =  write_xl(title_name_, data)
        return filepath

    except Exception, e:
        print "Excel, videos_info: ", str(e)
        return -1

    #update_data_info(title_name_, filepath)

def videos_info():
    try:
        title_name_ = "videos.xls"
        videos = Video.objects.all()
        row_title = ["课程题目", "类别", "关键词", 
                "价格", "视频数量", "观看人数", 
                "收藏人数", "评论数","有效期", "创建时间"]
        data = []
        data.append(row_title)
        if videos != None:
            for v in videos:
                row = []
                row.append(v.title)
                row.append(v.kind_str)
                row.append(v.tags_str)
                row.append(v.money)
                row.append(v.files_num)
                row.append(v.watch_num)
                row.append(v.share_num)
                row.append(v.comments_num)
                row.append(v.valid_day)
                row.append(str(v.release_date).split('+')[0])
                data.append(row)

        filepath =  write_xl(title_name_, data)
        return filepath

    except Exception, e:
        print "Excel, videos_info: ", str(e)
        return -1

    #update_data_info(title_name_, filepath)

def get_datainfo_given_title(title):
    data_info = DataInfo.objects.all()
    if getLen(data_info) > 0:
        for line in data_info:
            if line.title.encode('utf-8') == title:
                return line
    title_info = DataInfo()
    title_info.title = title
    title_info.filename = ""
    title_info.modify_datetime = str(datetime.datetime.now()).split('.')[0]
    title_info.save()
    return title_info


def update_data_info(title, filename):
    data_info = get_datainfo_given_title(title)
    data_info.title = title
    data_info.filename = filename 
    data_info.modify_datetime = str(datetime.datetime.now()).split('.')[0]
    data_info.save()
    

    
def write_xl(filename, data):
    file = xlwt.Workbook(encoding = 'utf-8')
    table = file.add_sheet('sheet_1')
    if data != None:
        for i in range(len(data)):
            for j in range(len(data[i])):
                table.write(i, j, data[i][j])

    #path =  DOWNLOAD_FOLD+filename + "-"+ getRandomStr() + ".xls"
    path =  DOWNLOAD_FOLD+filename

    file.save(path)
    return path

if __name__ == "__main__":
    videos_info()
