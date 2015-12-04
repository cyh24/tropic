#!/usr/bin/python
#-*- coding: utf-8 -*-
from models import *
import csv
from config import DOWNLOAD_FOLD
import xlwt
from common import getRandomStr, getLen, data_to_txt
from db_pro import get_unpay_num, get_paid_num, get_watch_history_num, get_collect_num
import datetime

def user_order_info():
    print "user order info..."
    try:
        title_name_ = "user_order_info.csv"
        user_order = UserOrderInfo.objects.all()
        row_title  = ['id', '昵称','视频名称','订单号', '价格', '是否付款', '下单时间', '是否PC登陆']
        data = []
        data.append(row_title)
        if getLen(user_order) > 0:
            for uo in user_order:
                row = []
                row.append(uo.id)
                row.append(uo.account.nickname)
                row.append(uo.order.video.title)
                row.append(uo.order.id)
                row.append(uo.order.price)
                if uo.order.pay_state == 2:
                    row.append('是')
                else:
                    row.append('否')

                row.append(str(uo.release_date).split('+')[0])
                if uo.pc_flag == 1:
                    row.append('是')
                else:
                    row.append('否')
                data.append(row)

        filepath =  write_csv(title_name_, data)
        return filepath

    except Exception, e:
        print "Excel, user_order_info: ", str(e)
        return -1


def user_watch_info():
    print "user watch info..."
    try:
        title_name_ = "user_watch_info.csv"
        user_watch = UserWatchInfo.objects.all()
        row_title  = ['id', '昵称','视频名称','观看时间', '是否PC登陆']
        data = []
        data.append(row_title)
        if getLen(user_watch) > 0:
            for uw in user_watch:
                row = []
                row.append(uw.id)
                row.append(uw.account.nickname)
                row.append(uw.video.title)
                row.append(str(uw.release_date).split('+')[0])
                if uw.pc_flag == 1:
                    row.append('是')
                else:
                    row.append('否')
                data.append(row)

        filepath =  write_csv(title_name_, data)
        return filepath

    except Exception, e:
        print "Excel, user_watch_info: ", str(e)
        return -1

    #update_data_info(title_name_, filepath)

def videos_info():
    try:
        title_name_ = "videos.csv"
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

        filepath =  write_csv(title_name_, data)
        return filepath

    except Exception, e:
        print "Excel, videos_info: ", str(e)
        return -1

    #update_data_info(title_name_, filepath)

def users_info():
    try:
        title_name_ = "users.csv"
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

        filepath =  write_csv(title_name_, data)
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


def write_csv(filename, data):
    st = ""
    if data != None:
        for i in range(len(data)):
            for j in range(len(data[i])):
                if type(data[i][j]) == type(u''):
                    data[i][j] = data[i][j].encode('utf-8')
                print data[i][j], type(data[i][j])
                st += "%s,"%str(data[i][j]).replace(',','，')
            st += "\n"

    path =  DOWNLOAD_FOLD+filename
    print st
    data_to_txt(path, st)
    return path


def write_xls(filename, data):
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
