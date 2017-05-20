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
        msg['usernames'] = names_str

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
        for i, name in enumerate(names):
            nn = name.strip('\n').strip()
            nn = nn.replace(',', '')
            if nn == "":
                nn = "NULL"
            names_str += nn + "-" + str(ids[i]) + "-=,"

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

        msg['exist_usernames'] = exist_usernames_str
        msg['card_name'] = card.card_name
        msg['img_path'] = card.img_path
        msg['valid_day'] = card.valid_day
        msg['card_id'] = int(card.id)
        msg['usernames'] = names_str

    except Exception, e:
        print "card update: ", str(e)

    return render_to_response('card/card_update.html', msg)

def set_card(card, card_name, img_path, ids, valid_day):
    with transaction.atomic():
        card.img_path = img_path
        card.card_name = card_name
        card.valid_day = valid_day
        card.save()
        card.allow_accounts.clear()
        for id in ids:
            card.allow_accounts.add(id)
        card.save()

def card_create_post(request):
    msg = {'state': 'fail'}
    try:
        card_name = request.POST['card_name']
        img_path = request.POST['img_path']
        valid_day = int(request.POST['valid_day'])
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
        card = Card()
        set_card(card, card_name, img_path, ids, valid_day)
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
            id_   = int(val[-1])
            ids.append(id_)

        card_id = int(request.POST['card_id'])
        img_path = request.POST['img_path']
        valid_day = int(request.POST['valid_day'])
        card = Card.objects.get(id=card_id)
        set_card(card, card_name, img_path, ids, valid_day)
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
