#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
import random
import datetime

def cards(request):
    msg = init_msg(request)
    cards = Card.objects.all()

    if getLen(cards) > 0:
        new_cards = []
        for v in cards:
            v.release_date = str(v.release_date).split(' ')[0]
            new_cards.append(v)
        cards = new_cards

    total_page = (getLen(cards)+10-1)/10
    subCards, cur_page = paginator_show(request, cards, 10)


    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['cards']     = subCards
    msg['cards_num'] = len(cards)
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1
    return render_to_response('card/cards.html', msg)

def get_usernames_ids():
    accounts = Account.objects.all()
    names = []
    ids   = []
    for acc in accounts:
        names.append(acc.nickname)
        ids.append(acc.id)
    return names, ids

def get_videonames_ids():
    videos = Video.objects.all()
    names = []
    ids   = []
    for v in videos:
        names.append(v.title)
        ids.append(v.id)
    return names, ids

@super_user
def card_create(request):
    msg = init_msg(request)
    msg['state'] = 'fail'
    try:
        names, ids = get_usernames_ids()
        names_str = ""
        for i, name in enumerate(names):
            nn = name.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            names_str += nn + "-" + str(ids[i]) + "-=,"

        video_names, video_ids = get_videonames_ids()
        video_names_str = ""
        for i, name in enumerate(video_names):
            # name = (name.encode('utf-8')).decode('utf-8')
            nn = name.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            video_names_str += nn + "-" + str(video_ids[i]) + "-=,"
        msg['usernames'] = names_str
        msg['videonames'] = video_names_str

    except Exception, e:
        print "card_create: ", str(e)

    return render_to_response('card/card_create.html', msg)

@super_user
def card_update(request):
    msg = init_msg(request)
    msg['state'] = 'fail'
    try:
        names, ids = get_usernames_ids()
        names_str = ""
        # print names
        for i, name in enumerate(names):
            nn = name.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            names_str += nn + "-" + str(ids[i]) + "-=,"


        video_names, video_ids = get_videonames_ids()
        video_names_str = ""
        for i, name in enumerate(video_names):
            # name = (name.encode('utf-8')).decode('utf-8')
            nn = name.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            video_names_str += nn + "-" + str(video_ids[i]) + "-=,"

        card_id = int(request.GET['card_id'])
        card = Card.objects.filter(id=card_id)[0]
        allow_accounts = card.allow_accounts.all()

        exist_usernames_str = ""
        for acc in allow_accounts:
            nn = acc.nickname
            nn = nn.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            exist_usernames_str += nn + "-" + str(acc.id) + "-=,"

        allow_videos = card.videos.all()
        exist_videonames_str = ""
        for v in allow_videos:
            nn = v.title
            nn = nn.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            exist_videonames_str += nn + "-" + str(v.id) + "-=,"

        msg['exist_usernames'] = exist_usernames_str
        msg['exist_videonames'] = exist_videonames_str
        msg['card_name'] = card.card_name
        msg['img_path'] = card.img_path
        msg['money'] = card.money
        msg['valid_day'] = card.valid_day
        msg['card_id'] = int(card.id)
        msg['usernames'] = names_str
        msg['videonames'] = video_names_str

    except Exception, e:
        print "card update: ", str(e)

    return render_to_response('card/card_update.html', msg)

def set_card(card, card_name, img_path, ids, video_ids, valid_day, money):
    with transaction.atomic():
        card.img_path = img_path
        card.card_name = card_name
        card.valid_day = valid_day
        card.money = money
        card.save()
        card.allow_accounts.clear()
        for id in video_ids:
            card.videos.add(id)
        for id in ids:
            card.allow_accounts.add(id)
        card.save()

def card_create_post(request):
    msg = {'state': 'fail'}
    try:
        card_name = request.POST['card_name']
        img_path = request.POST['img_path']
        valid_day = int(request.POST['valid_day'])
        money = float(request.POST['money'])
        if card_name.strip() == "":
            return render_to_response('info.html', msg)
        names = request.POST['names']
        names = names.split(',')
        ids = []
        for i, val in enumerate(names):
            val = val.split('-')
            try:
                id_   = int(val[-1])
                ids.append(id_)
            except Exception as e:
                printError(e)

        video_names = request.POST['video_names']
        video_names = video_names.split(',')
        video_ids = []
        for i, val in enumerate(video_names):
            val = val.split('-')
            try:
                id_   = int(val[-1])
                video_ids.append(id_)
            except Exception as e:
                printError(e)

        card = Card()
        set_card(card, card_name, img_path, ids, video_ids, valid_day, money)
        msg['state'] = 'ok'
    except Exception, e:
        print "Error in card_create_post:", e

    return render_to_response('info.html', msg)

def card_update_post(request):
    msg = {'state': 'fail'}
    try:
        card_name = request.POST['card_name']
        if card_name.strip() == "":
            return render_to_response('info.html', msg)
        names = request.POST['names']
        names = names.split(',')
        ids = []
        for i, val in enumerate(names):
            val = val.split('-')
            try:
                id_   = int(val[-1])
                ids.append(id_)
            except Exception as e:
                printError(e)

        video_names = request.POST['video_names']
        video_names = video_names.split(',')
        video_ids = []
        for i, val in enumerate(video_names):
            val = val.split('-')
            try:
                id_   = int(val[-1])
                video_ids.append(id_)
            except Exception as e:
                printError(e)

        card_id = int(request.POST['card_id'])
        img_path = request.POST['img_path']
        valid_day = int(request.POST['valid_day'])
        money = float(request.POST['money'])
        card = Card.objects.get(id=card_id)
        set_card(card, card_name, img_path, ids, video_ids, valid_day, money)
        msg['state'] = 'ok'
    except Exception, e:
        print "Error in card_update_post:", e

    return render_to_response('info.html', msg)

def db_delete_card(request):
    try:
        card_id = int(request.GET['card_id'])
        card = Card.objects.get(id=card_id)
        card.delete()
        return True
    except Exception, e:
        printError(e)
    return False

def card_delete(request):
    json = {'state': 'fail'}
    try:
        if request.GET.has_key('card_id'):
            if db_delete_card(request) == True:
                json = {'state': 'success'}
    except Exception, e:
        printError(e)
    return JsonResponse(json)
